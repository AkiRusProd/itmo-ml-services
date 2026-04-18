from functools import lru_cache

import joblib
import pandas as pd

from app.core.config import get_settings
from app.schemas.prediction import PredictionRequest


class ModelRegistry:
    def __init__(self) -> None:
        self.settings = get_settings()

    @lru_cache
    def load_model(self):
        model_path = self.settings.model_path
        if not model_path.exists():
            raise FileNotFoundError(model_path)
        return joblib.load(model_path)

    def predict(self, payload: PredictionRequest) -> float:
        model = self.load_model()
        features = pd.DataFrame([payload.to_model_features()])
        prediction = model.predict(features)[0]
        return float(prediction)

