from datetime import datetime

from pydantic import BaseModel, ConfigDict


class MLModelResponse(BaseModel):
    id: int
    name: str
    version: str
    artifact_path: str
    target_name: str
    features: list[str]
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(protected_namespaces=())
