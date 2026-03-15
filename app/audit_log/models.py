from enum import Enum
from uuid import UUID
from typing import Optional
from app.user.models import User
from sqlmodel import Field, Relationship
from app.database.models import BaseModel

class ActionEnum(Enum):
    COMMAND = "COMMAND"
    LOGIN = "LOGIN"
    RESET_ROBOT = "RESET_ROBOT"

class AuditLog(BaseModel, table=True):
    action: ActionEnum
    navigation_direction: Optional[str] = Field(nullable=True)
    user: User = Relationship(back_populates="audit_logs")
    user_id: UUID = Field(foreign_key="user.id", ondelete="CASCADE")