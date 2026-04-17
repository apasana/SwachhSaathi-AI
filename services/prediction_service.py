from __future__ import annotations

from functools import lru_cache
from random import Random

import numpy as np
from sklearn.linear_model import LinearRegression

from utils.helpers import risk_to_score, waste_to_score


class BinFillPredictor:
    def __init__(self):
        self.model = LinearRegression()
        self._fit_model()

    def _fit_model(self) -> None:
        rng = Random(42)
        samples = []
        targets = []

        for complaint_load in range(0, 60, 2):
            for risk_score in (1, 2, 3):
                for waste_score in (0.8, 1.0, 1.5):
                    noise = rng.uniform(-1.5, 1.5)
                    hours = max(2.0, 72 - (complaint_load * 0.75) - (risk_score * 8) - (waste_score * 6) + noise)
                    samples.append([complaint_load, risk_score, waste_score])
                    targets.append(hours)

        self.model.fit(np.array(samples), np.array(targets))

    def predict_fill_hours(self, complaint_load: int, risk_level: str, waste_type: str) -> float:
        features = np.array([[complaint_load, risk_to_score(risk_level), waste_to_score(waste_type)]])
        prediction = float(self.model.predict(features)[0])
        return round(max(1.0, prediction), 2)


@lru_cache(maxsize=1)
def get_predictor() -> BinFillPredictor:
    return BinFillPredictor()
