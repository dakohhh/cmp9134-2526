from pydantic import BaseModel

class Position(BaseModel):
    x: int
    y: int

class GetRobotStatusResponseSchema(BaseModel):
    position: Position