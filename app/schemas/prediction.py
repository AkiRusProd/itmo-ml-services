from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PredictionPayload(BaseModel):
    med_inc: float = Field(..., alias="MedInc", description="Median income in the district.")
    house_age: float = Field(..., alias="HouseAge", description="Median house age in the district.")
    ave_rooms: float = Field(..., alias="AveRooms", description="Average number of rooms.")
    ave_bedrms: float = Field(..., alias="AveBedrms", description="Average number of bedrooms.")
    population: float = Field(..., alias="Population", description="District population.")
    ave_occup: float = Field(..., alias="AveOccup", description="Average occupants per household.")
    latitude: float = Field(..., alias="Latitude", description="Latitude coordinate.")
    longitude: float = Field(..., alias="Longitude", description="Longitude coordinate.")
    cost_credits: int = Field(
        default=10,
        ge=1,
        le=1000,
        description="Prediction cost in internal credits. Defaults to 10 for the MVP.",
    )

    model_config = ConfigDict(populate_by_name=True, json_schema_extra={
        "example": {
            "MedInc": 8.3252,
            "HouseAge": 41.0,
            "AveRooms": 6.9841,
            "AveBedrms": 1.0238,
            "Population": 322.0,
            "AveOccup": 2.5556,
            "Latitude": 37.88,
            "Longitude": -122.23,
            "cost_credits": 10,
        }
    })

    def to_model_features(self) -> dict[str, float]:
        return {
            "MedInc": self.med_inc,
            "HouseAge": self.house_age,
            "AveRooms": self.ave_rooms,
            "AveBedrms": self.ave_bedrms,
            "Population": self.population,
            "AveOccup": self.ave_occup,
            "Latitude": self.latitude,
            "Longitude": self.longitude,
        }


class PredictionCreateResponse(BaseModel):
    id: int
    status: str
    task_id: str | None
    cost_credits: int
    prediction: float | None
    target_name: str | None
    model_name: str | None
    model_version: str | None

    model_config = ConfigDict(protected_namespaces=())


class PredictionListItem(BaseModel):
    id: int
    status: str
    task_id: str | None
    cost_credits: int
    created_at: datetime
    prediction: float | None
    model_name: str | None

    model_config = ConfigDict(protected_namespaces=())


class PredictionDetailResponse(BaseModel):
    id: int
    status: str
    task_id: str | None
    cost_credits: int
    input_payload: dict[str, float]
    error_message: str | None
    created_at: datetime
    updated_at: datetime
    prediction: float | None
    target_name: str | None
    model_name: str | None
    model_version: str | None

    model_config = ConfigDict(protected_namespaces=())
