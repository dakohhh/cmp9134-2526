from enum import Enum
from pydantic import BaseModel

class NavigationEnum(Enum):
    LEFT = "LEFT"
    RIGHT = "RIGHT"
    UP = "UP"
    DOWN = "DOWN"


class MoveRobotRequestSchema(BaseModel):
    navigation: NavigationEnum