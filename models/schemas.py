from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class WasteType(str, Enum):
    organic = "Organic"
    recyclable = "Recyclable"
    hazardous = "Hazardous"
    unknown = "Unknown"


class RiskLevel(str, Enum):
    low = "Low"
    medium = "Medium"
    high = "High"


class ComplaintStatus(str, Enum):
    new = "new"
    under_review = "under_review"
    assigned = "assigned"
    resolved = "resolved"


class UserRole(str, Enum):
    citizen = "citizen"
    authority = "authority"


class ComplaintCreate(BaseModel):
    description: str = Field(..., min_length=3, description="Text description of the waste issue")
    location: str = Field(..., min_length=2, description="Ward, street, or landmark")
    citizen_name: Optional[str] = Field(default=None, description="Optional reporter name")
    contact_number: Optional[str] = Field(default=None, description="Optional contact number")
    image_base64: Optional[str] = Field(default=None, description="Optional base64 image payload")
    reported_via: str = Field(default="web", description="Source channel for the complaint")


class ComplaintUpdate(BaseModel):
    status: ComplaintStatus
    assigned_to: Optional[str] = None
    authority_notes: Optional[str] = None


class ComplaintRecord(BaseModel):
    id: Optional[str] = None
    ticket_id: str
    description: str
    location: str
    citizen_name: Optional[str] = None
    contact_number: Optional[str] = None
    reported_via: str
    waste_type: WasteType
    waste_type_confidence: float
    risk_level: RiskLevel
    issue_type: str
    predicted_bin_fill_hours: float
    status: ComplaintStatus
    ai_source: str
    image_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    metadata: dict = Field(default_factory=dict)


class ComplaintResponse(BaseModel):
    success: bool = True
    message: str
    data: ComplaintRecord


class TrackingResponse(BaseModel):
    success: bool = True
    ticket_id: str
    status: ComplaintStatus
    risk_level: RiskLevel
    waste_type: WasteType
    predicted_bin_fill_hours: float
    last_updated: datetime


class DashboardMetrics(BaseModel):
    total_complaints: int
    resolved_complaints: int
    pending_complaints: int
    high_risk_complaints: int
    average_fill_time_hours: float


class DashboardSummary(BaseModel):
    metrics: DashboardMetrics
    waste_distribution: dict[str, int]
    risk_distribution: dict[str, int]
    status_distribution: dict[str, int]
    predicted_alerts: list[dict]
    recent_complaints: list[dict]


class HealthResponse(BaseModel):
    status: str
    service: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)
    password: str = Field(..., min_length=6, max_length=64)
    full_name: str = Field(..., min_length=2, max_length=80)
    contact_number: str = Field(..., min_length=8, max_length=20)
    role: UserRole = UserRole.citizen


class UserLogin(BaseModel):
    username: str
    password: str


class UserPublic(BaseModel):
    username: str
    full_name: str
    contact_number: str
    role: UserRole


class AuthResponse(BaseModel):
    success: bool = True
    message: str
    data: UserPublic
