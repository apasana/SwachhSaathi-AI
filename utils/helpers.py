import base64
import os
from datetime import datetime
from typing import Any
from uuid import uuid4

from bson import ObjectId

from utils.config import settings


RISK_TO_SCORE = {"Low": 1, "Medium": 2, "High": 3}
WASTE_TO_SCORE = {"Organic": 1.0, "Recyclable": 0.8, "Hazardous": 1.5, "Unknown": 1.1}


def ensure_upload_folder() -> None:
    os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)


def save_image(image_file, filename: str) -> str:
    ensure_upload_folder()
    path = os.path.join(settings.UPLOAD_FOLDER, filename)
    image_file.save(path)
    return path


def generate_ticket_id() -> str:
    return f"SSA-{datetime.utcnow().strftime('%Y%m%d')}-{uuid4().hex[:8].upper()}"


def validate_report_payload(text: str | None, location: str | None, image_present: bool) -> tuple[bool, str]:
    if not text and not image_present:
        return False, "Either a description or an image is required"
    if not location:
        return False, "Location is required"
    return True, ""


def decode_base64_image(image_base64: str) -> bytes:
    payload = image_base64.split(",", 1)[-1]
    return base64.b64decode(payload)


def object_id_to_str(value: Any) -> Any:
    if isinstance(value, ObjectId):
        return str(value)
    return value


def serialize_document(document: dict[str, Any]) -> dict[str, Any]:
    serialized = {}
    for key, value in document.items():
        if isinstance(value, ObjectId):
            serialized[key] = str(value)
        elif isinstance(value, dict):
            serialized[key] = serialize_document(value)
        elif isinstance(value, list):
            serialized[key] = [serialize_document(item) if isinstance(item, dict) else object_id_to_str(item) for item in value]
        else:
            serialized[key] = object_id_to_str(value)
    return serialized


def risk_to_score(risk_level: str) -> int:
    return RISK_TO_SCORE.get(risk_level, 1)


def waste_to_score(waste_type: str) -> float:
    return WASTE_TO_SCORE.get(waste_type, 1.0)


def build_storage_filename(prefix: str, extension: str) -> str:
    return f"{prefix}_{uuid4().hex}{extension}"