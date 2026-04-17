from __future__ import annotations

from datetime import datetime
from io import BytesIO
from pathlib import Path

from fastapi import HTTPException
from PIL import Image

from database.mongo import MongoConnectionError, get_complaints_collection
from models.schemas import ComplaintCreate, ComplaintStatus
from services.ai_service import AIService
from services.prediction_service import get_predictor
from utils.config import settings
from utils.helpers import (
    build_storage_filename,
    decode_base64_image,
    generate_ticket_id,
    serialize_document,
    validate_report_payload,
)


class ComplaintService:
    def __init__(self):
        self.ai_service = AIService()
        self.predictor = get_predictor()

    def create_complaint(self, payload: ComplaintCreate, image_bytes: bytes | None = None, image_filename: str | None = None) -> dict:
        image_present = image_bytes is not None or payload.image_base64 is not None
        is_valid, error_message = validate_report_payload(payload.description, payload.location, image_present)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_message)

        try:
            collection = get_complaints_collection()
        except MongoConnectionError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

        text_result = self.ai_service.analyze_text(payload.description)
        image_result = None
        saved_image_path = None

        if payload.image_base64:
            image_bytes = decode_base64_image(payload.image_base64)

        if image_bytes:
            image_result = self.ai_service.analyze_image(image_bytes)
            saved_image_path = self._save_image(image_bytes, image_filename)

        combined = self.ai_service.combine_signals(text_result, image_result)

        complaint_count = collection.count_documents({"location": payload.location}) + 1
        predicted_fill_hours = self.predictor.predict_fill_hours(
            complaint_count,
            combined["risk_level"],
            combined["waste_type"],
        )

        created_at = datetime.utcnow()
        document = {
            "ticket_id": generate_ticket_id(),
            "description": payload.description,
            "location": payload.location,
            "citizen_name": payload.citizen_name,
            "contact_number": payload.contact_number,
            "reported_via": payload.reported_via,
            "waste_type": combined["waste_type"],
            "waste_type_confidence": combined["waste_type_confidence"],
            "risk_level": combined["risk_level"],
            "issue_type": combined["issue_type"],
            "predicted_bin_fill_hours": predicted_fill_hours,
            "status": ComplaintStatus.new.value,
            "ai_source": combined["ai_source"],
            "matched_keywords": combined["matched_keywords"],
            "image_path": saved_image_path,
            "created_at": created_at,
            "updated_at": created_at,
            "metadata": {
                "complaints_in_location": complaint_count,
                "text_confidence": text_result.get("confidence", 0.0),
            },
        }

        insert_result = collection.insert_one(document)
        document["_id"] = insert_result.inserted_id
        document["id"] = str(insert_result.inserted_id)

        return serialize_document(document)

    def list_complaints(self, query: dict | None = None, limit: int = 50) -> list[dict]:
        try:
            collection = get_complaints_collection()
        except MongoConnectionError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

        cursor = collection.find(query or {}).sort("created_at", -1).limit(limit)
        return [serialize_document(item) for item in cursor]

    def get_complaint(self, ticket_id: str) -> dict:
        try:
            collection = get_complaints_collection()
        except MongoConnectionError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

        complaint = collection.find_one({"ticket_id": ticket_id})
        if not complaint:
            raise HTTPException(status_code=404, detail="Complaint not found")
        return serialize_document(complaint)

    def update_status(self, ticket_id: str, status: str, assigned_to: str | None = None, authority_notes: str | None = None) -> dict:
        try:
            collection = get_complaints_collection()
        except MongoConnectionError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

        update_fields = {
            "status": status,
            "updated_at": datetime.utcnow(),
        }
        if assigned_to:
            update_fields["assigned_to"] = assigned_to
        if authority_notes:
            update_fields["authority_notes"] = authority_notes

        result = collection.update_one({"ticket_id": ticket_id}, {"$set": update_fields})
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Complaint not found")

        return self.get_complaint(ticket_id)

    def dashboard_records(self) -> list[dict]:
        return self.list_complaints(limit=200)

    def _save_image(self, image_bytes: bytes, image_filename: str | None) -> str:
        from utils.helpers import ensure_upload_folder

        ensure_upload_folder()
        extension = Path(image_filename or "complaint.png").suffix or ".png"
        target_name = build_storage_filename("complaint", extension)
        target_path = Path(settings.UPLOAD_FOLDER) / target_name
        with Image.open(BytesIO(image_bytes)) as image:
            image.convert("RGB").save(target_path)
        return str(target_path)


complaint_service = ComplaintService()
