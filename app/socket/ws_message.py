from enum import Enum
from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")

class WsMessageType(str, Enum):
    TELEMETRY = "TELEMETRY"
    ERROR = "ERROR"

class WsMessage(BaseModel, Generic[T]):
    type: WsMessageType
    data: T
