from pydantic import BaseModel

class GetMapResponse(BaseModel):
    width: int
    height: int
    grid: list[list[int]]