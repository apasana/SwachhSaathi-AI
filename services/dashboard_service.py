from __future__ import annotations

from collections import Counter


class DashboardService:
    def build_summary(self, complaints: list[dict]) -> dict:
        total = len(complaints)
        resolved = sum(1 for item in complaints if item.get("status") == "resolved")
        pending = total - resolved
        high_risk = sum(1 for item in complaints if item.get("risk_level") == "High")

        waste_distribution = Counter(item.get("waste_type", "Unknown") for item in complaints)
        risk_distribution = Counter(item.get("risk_level", "Low") for item in complaints)
        status_distribution = Counter(item.get("status", "new") for item in complaints)

        average_fill_time = 0.0
        if complaints:
            average_fill_time = round(sum(float(item.get("predicted_bin_fill_hours", 0)) for item in complaints) / total, 2)

        predicted_alerts = [
            {
                "ticket_id": item.get("ticket_id"),
                "location": item.get("location"),
                "risk_level": item.get("risk_level"),
                "predicted_bin_fill_hours": item.get("predicted_bin_fill_hours"),
                "alert": "Immediate inspection required"
                if item.get("risk_level") == "High" or float(item.get("predicted_bin_fill_hours", 0)) <= 12
                else "Monitor",
            }
            for item in complaints
            if item.get("risk_level") == "High" or float(item.get("predicted_bin_fill_hours", 0)) <= 18
        ]

        recent_complaints = sorted(complaints, key=lambda item: item.get("created_at", ""), reverse=True)[:10]

        return {
            "metrics": {
                "total_complaints": total,
                "resolved_complaints": resolved,
                "pending_complaints": pending,
                "high_risk_complaints": high_risk,
                "average_fill_time_hours": average_fill_time,
            },
            "waste_distribution": dict(waste_distribution),
            "risk_distribution": dict(risk_distribution),
            "status_distribution": dict(status_distribution),
            "predicted_alerts": predicted_alerts,
            "recent_complaints": recent_complaints,
        }


dashboard_service = DashboardService()
