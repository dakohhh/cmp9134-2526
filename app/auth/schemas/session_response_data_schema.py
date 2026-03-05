from pydantic import BaseModel
from app.user.models import RoleEnum

class SessionResponseDataSchema(BaseModel):
    full_name: str
    email: str
    role: RoleEnum





