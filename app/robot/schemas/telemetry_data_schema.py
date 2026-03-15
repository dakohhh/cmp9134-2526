from pydantic import BaseModel
from typing import List, Literal


class TelemetryDataPosition(BaseModel):
    x: int
    y: int

TelemetryDataStatus = Literal["IDLE", "MOVING", "LOW_BATTERY", "STUCK"]

class TelemetrySensorsSchema(BaseModel):
    N: int
    S: int
    E: int
    W: int
    lidar: List[float]

class TelemetryDataSchema(BaseModel):
    position: TelemetryDataPosition
    battery: float
    status: TelemetryDataStatus
    sensors: TelemetrySensorsSchema
 