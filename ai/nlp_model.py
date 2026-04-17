import re
import string


STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "but",
    "by",
    "for",
    "if",
    "in",
    "into",
    "is",
    "it",
    "no",
    "not",
    "of",
    "on",
    "or",
    "such",
    "that",
    "the",
    "their",
    "then",
    "there",
    "these",
    "they",
    "this",
    "to",
    "was",
    "will",
    "with",
}


def _tokenize(text: str) -> list[str]:
    clean_text = re.sub(r"[^a-zA-Z0-9\s]", " ", text.lower())
    return [word for word in clean_text.split() if word not in STOPWORDS and word not in string.punctuation]


def analyze_complaint_details(text: str) -> dict:
    tokens = _tokenize(text)
    normalized = text.lower()

    issue_type = "General"
    risk_level = "Low"
    confidence = 0.58
    matched_keywords: list[str] = []

    if any(keyword in normalized for keyword in ["missed", "pickup", "did not come", "not collected"]) or {"nahi", "aaya"}.issubset(set(tokens)):
        issue_type = "Missed Pickup"
        risk_level = "High"
        confidence = 0.91
        matched_keywords = [keyword for keyword in ["missed", "pickup", "did not come", "not collected", "nahi", "aaya"] if keyword in normalized or keyword in tokens]
    elif any(keyword in normalized for keyword in ["overflow", "full", "overflowing", "bhara"]):
        issue_type = "Overflow"
        risk_level = "Medium"
        confidence = 0.86
        matched_keywords = [keyword for keyword in ["overflow", "full", "overflowing", "bhara"] if keyword in normalized or keyword in tokens]
    elif any(keyword in normalized for keyword in ["hazard", "chemical", "medical", "toxic", "battery"]):
        issue_type = "Hazardous Waste"
        risk_level = "High"
        confidence = 0.89
        matched_keywords = [keyword for keyword in ["hazard", "chemical", "medical", "toxic", "battery"] if keyword in normalized or keyword in tokens]
    elif any(keyword in normalized for keyword in ["clean", "garbage", "litter", "dustbin", "smell"]):
        issue_type = "General Waste"
        risk_level = "Low"
        confidence = 0.72
        matched_keywords = [keyword for keyword in ["garbage", "litter", "dustbin", "smell"] if keyword in normalized]

    return {
        "issue_type": issue_type,
        "risk_level": risk_level,
        "confidence": round(confidence, 2),
        "matched_keywords": matched_keywords,
        "tokens": tokens,
    }


def analyze_complaint(text: str):
    details = analyze_complaint_details(text)
    return details["issue_type"], details["risk_level"]