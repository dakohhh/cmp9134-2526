from pydantic import EmailStr, Field
from pydantic import BaseModel
from typing import Annotated
from annotated_types import MinLen, MaxLen

class RegisterSchema(BaseModel):
    full_name: str = Field(examples=["Wisdom Dakoh"])
    email: EmailStr = Field(examples=["wisdomdakoh@gmail.com"])
    password: Annotated[str, MinLen(8), MaxLen(64)] = Field(examples=["wisdomdakoh12"])
