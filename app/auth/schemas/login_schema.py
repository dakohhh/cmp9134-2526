from pydantic import BaseModel, EmailStr, Field

class LoginSchema(BaseModel):
    email: EmailStr = Field(examples=["wisdomdakoh@gmail.com"])
    password: str = Field(examples=["wisdom"])