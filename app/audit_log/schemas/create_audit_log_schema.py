from typing import Optional
from pydantic import BaseModel
from ..models import ActionEnum

class CreateAuditLogSchema(BaseModel):
    action: ActionEnum
    navigation_direction: Optional[str] = None