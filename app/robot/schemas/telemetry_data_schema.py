from pydantic import BaseModel

class TelemetryDataPosition(BaseModel):
    x: int
    y: int
class TelemetryDataSchema(BaseModel):
    position: TelemetryDataPosition
    battery: float
    status: str