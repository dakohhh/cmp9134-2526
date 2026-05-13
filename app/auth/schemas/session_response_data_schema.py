import uuid
from pydantic import BaseModel
from app.user.models import RoleEnum

class SessionResponseDataSchema(BaseModel):
    id: uuid.UUID
    full_name: str
    email: str
    role: RoleEnum





