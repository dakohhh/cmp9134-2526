from pydantic import BaseModel


class RegisterSchema(BaseModel):
    full_first: str