from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, Any


class SensorReadingSchema(BaseModel):
    device_id: str = Field(..., description="Unique ID of the IoT device")
    # Water quality parameters — all optional; device may not report all
    do: Optional[float] = Field(None, description="Dissolved oxygen (mg/L)")
    ph: Optional[float] = Field(None, description="pH level")
    temp: Optional[float] = Field(None, description="Temperature (°C)")
    salinity: Optional[float] = Field(None, description="Salinity (ppt)")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Reading timestamp (UTC)")
    raw_payload: Optional[dict[str, Any]] = Field(None, description="Full raw payload from device")

    model_config = {"json_schema_extra": {"example": {
        "device_id": "WQ-001",
        "do": 6.5,
        "ph": 7.2,
        "temp": 29.5,
        "salinity": 30.1,
        "timestamp": "2026-05-31T10:00:00Z",
        "raw_payload": {"device": "WQ-001", "battery": 85},
    }}}


class SensorReadingResponse(BaseModel):
    success: bool
    message: str
    device_id: str
