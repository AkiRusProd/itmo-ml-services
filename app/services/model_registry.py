from functools import lru_cache

import joblib
import pandas as pd

from app.core.config import get_settings
from app.schemas.prediction import PredictionPayload


class ModelRegistry:
    def __init__(self) -> None:
        self.settings = get_settings()

    @lru_cache
    def load_model(self):
        model_path = self.settings.model_path
        if not model_path.exists():
            raise FileNotFoundError(model_path)
        return joblib.load(model_path)

    def predict(self, payload: PredictionPayload) -> float:
        model = self.load_model()
        features = pd.DataFrame([payload.to_model_features()])
        prediction = model.predict(features)[0]
        return float(prediction)

    def get_metadata(self) -> dict[str, str]:
        return {
            "target_name": "MedHouseVal",
            "model_name": "apartment_price_model",
            "model_version": "v1",
        }
