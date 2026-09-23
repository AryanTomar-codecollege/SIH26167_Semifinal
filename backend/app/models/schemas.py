from typing import Any, Dict, List
from pydantic import BaseModel, Field


class GeoJSON(BaseModel):
    type: str = "FeatureCollection"
    features: List[Dict[str, Any]] = Field(default_factory=list)


class ExecutionTrace(BaseModel):
    selected_task: str
    tools_used: List[str] = Field(default_factory=list)
    model_used: str
    parameters: Dict[str, Any] = Field(default_factory=dict)


class Metadata(BaseModel):
    num_images: int
    modalities: List[str]
    crs: str


class SuccessResponse(BaseModel):
    success: bool = True
    answer: str
    geojson: GeoJSON
    confidence: float = Field(ge=0.0, le=1.0)
    execution_trace: ExecutionTrace
    metadata: Metadata


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    error_code: str
