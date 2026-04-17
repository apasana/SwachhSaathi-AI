from __future__ import annotations

from fastapi import APIRouter, File, Form, UploadFile

from models.schemas import ComplaintCreate, ComplaintRecord, ComplaintResponse, ComplaintStatus, ComplaintUpdate, TrackingResponse
from services.complaint_service import complaint_service


router = APIRouter(prefix="/complaints", tags=["Complaints"])


@router.post("", response_model=ComplaintResponse)
def create_complaint(payload: ComplaintCreate):
    complaint = complaint_service.create_complaint(payload)
    return ComplaintResponse(message="Complaint submitted successfully", data=ComplaintRecord(**complaint))


@router.post("/upload", response_model=ComplaintResponse)
async def create_complaint_with_image(
    description: str = Form(...),
    location: str = Form(...),
    citizen_name: str | None = Form(None),
    contact_number: str | None = Form(None),
    reported_via: str = Form("mobile"),
    image: UploadFile | None = File(None),
):
    payload = ComplaintCreate(
        description=description,
        location=location,
        citizen_name=citizen_name,
        contact_number=contact_number,
        reported_via=reported_via,
    )
    image_bytes = await image.read() if image else None
    complaint = complaint_service.create_complaint(payload, image_bytes=image_bytes, image_filename=image.filename if image else None)
    return ComplaintResponse(message="Complaint submitted successfully", data=ComplaintRecord(**complaint))


@router.get("", response_model=list[ComplaintRecord])
def list_complaints(limit: int = 50, contact_number: str | None = None):
    query = {"contact_number": contact_number} if contact_number else None
    complaints = complaint_service.list_complaints(query=query, limit=limit)
    return [ComplaintRecord(**item) for item in complaints]


@router.get("/history/{contact_number}", response_model=list[ComplaintRecord])
def complaint_history(contact_number: str, limit: int = 100):
    complaints = complaint_service.list_complaints(query={"contact_number": contact_number}, limit=limit)
    return [ComplaintRecord(**item) for item in complaints]


@router.get("/{ticket_id}", response_model=TrackingResponse)
def track_complaint(ticket_id: str):
    complaint = complaint_service.get_complaint(ticket_id)
    return TrackingResponse(
        ticket_id=complaint["ticket_id"],
        status=ComplaintStatus(complaint["status"]),
        risk_level=complaint["risk_level"],
        waste_type=complaint["waste_type"],
        predicted_bin_fill_hours=complaint["predicted_bin_fill_hours"],
        last_updated=complaint["updated_at"],
    )


@router.patch("/{ticket_id}/status", response_model=ComplaintResponse)
def update_complaint_status(ticket_id: str, payload: ComplaintUpdate):
    complaint = complaint_service.update_status(ticket_id, payload.status.value, payload.assigned_to, payload.authority_notes)
    return ComplaintResponse(message="Complaint status updated", data=ComplaintRecord(**complaint))
