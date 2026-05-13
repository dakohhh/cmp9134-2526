from uuid import UUID
from pydantic import BaseModel
from ..models import ActionEnum
from typing import List, Optional
from app.common.paginator import PageNumberPaginatorMeta

class User(BaseModel):
    id: UUID
    full_name: str

class AuditLog(BaseModel,):
    action: ActionEnum
    navigation_direction: Optional[str] = None
    user: User
    user_id: UUID


class GetAllAuditLogResponseDataSchema(BaseModel):
    results: List[AuditLog]
    meta: PageNumberPaginatorMeta
