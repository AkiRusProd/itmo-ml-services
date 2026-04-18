from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.ml_model import MLModel
from app.schemas.ml_model import MLModelResponse
from app.services.model_registry import ModelRegistry


class MLModelService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.settings = get_settings()

    def ensure_current_model_registered(self) -> MLModel:
        metadata = ModelRegistry.get_static_metadata(self.settings.model_path)
        statement = select(MLModel).where(MLModel.is_active.is_(True))
        current_model = self.db.execute(statement).scalar_one_or_none()

        if current_model is None:
            current_model = MLModel(
                name=metadata["model_name"],
                version=metadata["model_version"],
                artifact_path=str(self.settings.model_path),
                target_name=metadata["target_name"],
                features_json=metadata["features"],
                is_active=True,
            )
            self.db.add(current_model)
            self.db.commit()
            self.db.refresh(current_model)
            return current_model

        has_changes = any(
            [
                current_model.name != metadata["model_name"],
                current_model.version != metadata["model_version"],
                current_model.artifact_path != str(self.settings.model_path),
                current_model.target_name != metadata["target_name"],
                current_model.features_json != metadata["features"],
            ]
        )
        if has_changes:
            current_model.name = metadata["model_name"]
            current_model.version = metadata["model_version"]
            current_model.artifact_path = str(self.settings.model_path)
            current_model.target_name = metadata["target_name"]
            current_model.features_json = metadata["features"]
            self.db.commit()
            self.db.refresh(current_model)
        return current_model

    def get_current_model(self) -> MLModelResponse:
        current_model = self.db.execute(
            select(MLModel).where(MLModel.is_active.is_(True))
        ).scalar_one_or_none()
        if current_model is None:
            current_model = self.ensure_current_model_registered()
        return MLModelResponse(
            id=current_model.id,
            name=current_model.name,
            version=current_model.version,
            artifact_path=current_model.artifact_path,
            target_name=current_model.target_name,
            features=list(current_model.features_json),
            is_active=current_model.is_active,
            created_at=current_model.created_at,
        )
