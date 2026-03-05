from pydantic import BaseModel
from app.user.models import RoleEnum

class UpdateUserRoleSchema(BaseModel):
    role: RoleEnum