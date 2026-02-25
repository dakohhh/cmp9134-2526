from pydantic import BaseModel

class SessionResponseDataSchema(BaseModel):
    is_staff: bool
    full_name: str




