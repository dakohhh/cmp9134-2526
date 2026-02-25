from pydantic import BaseModel, EmailStr, Field

class RequestPasswordResetSchema(BaseModel):
    email: EmailStr = Field(examples=["wisdomdakoh@gmail.com"])