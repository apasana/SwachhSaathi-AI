from __future__ import annotations

from dataclasses import asdict

from ai.cv_model import classify_waste_detailed, get_classifier
from ai.nlp_model import analyze_complaint_details
from utils.config import settings


class AIService:
    def __init__(self):
        self.image_classifier = get_classifier(settings.TF_MODEL_PATH)

    def analyze_text(self, description: str) -> dict:
        return analyze_complaint_details(description)

    def analyze_image(self, image_input) -> dict:
        result = classify_waste_detailed(image_input)
        return asdict(result)

    def combine_signals(self, text_result: dict, image_result: dict | None) -> dict:
        waste_type = image_result["waste_type"] if image_result and image_result.get("waste_type") != "Unknown" else self._waste_from_text(text_result)
        risk_level = text_result.get("risk_level", "Low")

        if waste_type == "Hazardous":
            risk_level = "High"
        elif waste_type == "Organic" and risk_level == "Low":
            risk_level = "Medium"

        return {
            "issue_type": text_result.get("issue_type", "General"),
            "text_risk_level": text_result.get("risk_level", "Low"),
            "risk_level": risk_level,
            "waste_type": waste_type,
            "waste_type_confidence": (image_result or {}).get("confidence", 0.0),
            "ai_source": (image_result or {}).get("source", "text-only") if image_result else "text-only",
            "matched_keywords": text_result.get("matched_keywords", []),
        }

    def _waste_from_text(self, text_result: dict) -> str:
        issue_type = text_result.get("issue_type", "General")
        if issue_type == "Hazardous Waste":
            return "Hazardous"
        if issue_type == "Overflow":
            return "Organic"
        return "Unknown"
