from uuid import UUID
from typing  import Optional
from sqlmodel import SQLModel


class RegisterResponseDataSchema(SQLModel):
    id: UUID
    email: str
    first_name: str
    last_name: str
    middle_name: Optional[str]