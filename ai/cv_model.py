from __future__ import annotations

import io
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

try:
    from tensorflow.keras.models import load_model
except Exception:  # pragma: no cover
    load_model = None


@dataclass
class WasteClassificationResult:
    waste_type: str
    confidence: float
    source: str


class WasteImageClassifier:
    """TensorFlow-first image classifier with a safe heuristic fallback."""

    def __init__(self, model_path: str | None = None):
        self.model_path = model_path
        self.model = None
        self._load_model()

    def _load_model(self) -> None:
        if load_model is None or not self.model_path:
            return
        model_file = Path(self.model_path)
        if model_file.exists():
            try:
                self.model = load_model(model_file)
            except Exception:
                self.model = None

    def classify(self, image_input: Any) -> WasteClassificationResult:
        image = self._load_image(image_input)
        if image is None:
            return WasteClassificationResult("Unknown", 0.0, "invalid-image")

        if self.model is not None:
            try:
                return self._predict_with_tensorflow(image)
            except Exception:
                pass

        return self._heuristic_classify(image)

    def _load_image(self, image_input: Any) -> Image.Image | None:
        try:
            if isinstance(image_input, (str, Path)):
                return Image.open(image_input).convert("RGB")
            if isinstance(image_input, bytes):
                return Image.open(io.BytesIO(image_input)).convert("RGB")
            if hasattr(image_input, "read"):
                return Image.open(image_input).convert("RGB")
        except Exception:
            return None
        return None

    def _predict_with_tensorflow(self, image: Image.Image) -> WasteClassificationResult:
        resized = image.resize((224, 224))
        array = np.asarray(resized, dtype=np.float32) / 255.0
        batch = np.expand_dims(array, axis=0)
        predictions = self.model.predict(batch, verbose=0)
        class_index = int(np.argmax(predictions[0]))
        confidence = float(np.max(predictions[0]))

        label_map = {0: "Organic", 1: "Recyclable", 2: "Hazardous"}
        return WasteClassificationResult(label_map.get(class_index, "Unknown"), round(confidence, 2), "tensorflow")

    def _heuristic_classify(self, image: Image.Image) -> WasteClassificationResult:
        rgb = np.asarray(image, dtype=np.float32)
        mean_red = float(np.mean(rgb[:, :, 0]))
        mean_green = float(np.mean(rgb[:, :, 1]))
        mean_blue = float(np.mean(rgb[:, :, 2]))

        if mean_red > mean_green + 20 and mean_red > mean_blue + 20:
            return WasteClassificationResult("Hazardous", 0.64, "heuristic-color")
        if mean_green >= mean_red and mean_green >= mean_blue:
            return WasteClassificationResult("Organic", 0.62, "heuristic-color")
        return WasteClassificationResult("Recyclable", 0.60, "heuristic-color")


_classifier: WasteImageClassifier | None = None


def get_classifier(model_path: str | None = None) -> WasteImageClassifier:
    global _classifier
    if _classifier is None:
        _classifier = WasteImageClassifier(model_path=model_path)
    return _classifier


def classify_waste(image_path):
    return get_classifier().classify(image_path).waste_type


def classify_waste_detailed(image_input):
    return get_classifier().classify(image_input)