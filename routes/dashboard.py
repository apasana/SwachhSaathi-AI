from __future__ import annotations

from fastapi import APIRouter

from models.schemas import DashboardMetrics, DashboardSummary
from services.complaint_service import complaint_service
from services.dashboard_service import dashboard_service


router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def dashboard_summary():
    records = complaint_service.dashboard_records()
    summary = dashboard_service.build_summary(records)
    return DashboardSummary(
        metrics=DashboardMetrics(**summary["metrics"]),
        waste_distribution=summary["waste_distribution"],
        risk_distribution=summary["risk_distribution"],
        status_distribution=summary["status_distribution"],
        predicted_alerts=summary["predicted_alerts"],
        recent_complaints=summary["recent_complaints"],
    )


@router.get("/alerts")
def dashboard_alerts():
    records = complaint_service.dashboard_records()
    return dashboard_service.build_summary(records)["predicted_alerts"]
