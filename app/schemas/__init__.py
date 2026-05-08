from pydantic import BaseModel, ConfigDict, Field
from typing import Optional


class TrainSchema(BaseModel):
    weight: float = Field(..., gt=0, description="Train weight in tons")
    train_cars: int = Field(..., gt=0, description="Number of train cars")
    length: Optional[float] = Field(None, gt=0, description="Train length in meters")

    model_config = ConfigDict(extra='forbid')


class TrackSchema(BaseModel):
    length: float = Field(..., gt=0, le=100000, description="Segment length in meters")
    bending: float = Field(..., ge=0, le=90, description="Curve radius or degrees of curvature")
    elevation: float = Field(..., ge=0, description="Elevation change in meters")

    model_config = ConfigDict(extra='forbid')


class SimulationRequest(BaseModel):
    train: TrainSchema
    line: dict = Field(..., description="Line metadata including total_length")
    tracks: list[TrackSchema] = Field(..., min_length=1)

    model_config = ConfigDict(extra='forbid', json_schema_extra={
        "example": {
            "train": {"weight": 2000, "train_cars": 12},
            "line": {"total_length": 12000},
            "tracks": [{"length": 500, "bending": 5, "elevation": 100}]
        }
    })


class SimulationPoint(BaseModel):
    track_index: int
    distance: float
    electricity_usage: float
    track: TrackSchema


class SimulationResponse(BaseModel):
    total_energy: float = Field(..., description="Total energy consumption in kWh")
    average_energy: float = Field(..., description="Average energy per meter in kWh/m")
    points: list[SimulationPoint] = Field(..., description="Per-segment energy breakdown")
