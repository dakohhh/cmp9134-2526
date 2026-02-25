from pydantic import BaseModel, EmailStr

class ResetPasswordVerifySchema(BaseModel):
    email: EmailStr
    token: str