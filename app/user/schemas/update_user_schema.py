from typing import Optional
from pydantic import BaseModel

class UpdateUserSchema(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None

    