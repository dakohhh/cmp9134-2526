import uuid
from pydantic import BaseModel
from app.user.models import RoleEnum
from typing import List
from app.common.paginator import PageNumberPaginatorMeta


class UserEntry(BaseModel):
    id: uuid.UUID
    full_name: str | None
    email: str
    role: RoleEnum


class GetAllUsersResponseSchema(BaseModel):
    results: List[UserEntry]
    meta: PageNumberPaginatorMeta
