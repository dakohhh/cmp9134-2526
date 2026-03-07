from pydantic import BaseModel, PositiveInt

class Position(BaseModel):
    x: PositiveInt
    y: PositiveInt

class MoveRobotResponseSchema(BaseModel):
    position: Position