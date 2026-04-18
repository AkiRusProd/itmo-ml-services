from dataclasses import dataclass
from uuid import uuid4

from app.schemas.prediction import PredictionPayload
from app.services.model_registry import ModelRegistry


@dataclass
class PredictionTaskResult:
    task_id: str
    prediction_value: float
    target_name: str
    model_name: str
    model_version: str


class PredictionTaskDispatcher:
    def dispatch_inline(self, payload: PredictionPayload) -> PredictionTaskResult:
        model_registry = ModelRegistry()
        prediction_value = model_registry.predict(payload)
        metadata = model_registry.get_metadata()
        return PredictionTaskResult(
            task_id=f"inline-{uuid4()}",
            prediction_value=prediction_value,
            target_name=metadata["target_name"],
            model_name=metadata["model_name"],
            model_version=metadata["model_version"],
        )
