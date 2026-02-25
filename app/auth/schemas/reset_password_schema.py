from pydantic import BaseModel, EmailStr, Field

class ResetPasswordSchema(BaseModel):
    email: EmailStr = Field(examples=["wisdomdakoh@gmail.com"])
    token: str
    new_password: str