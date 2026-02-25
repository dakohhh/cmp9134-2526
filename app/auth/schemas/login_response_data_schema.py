from pydantic import BaseModel

class LoginResponseDataSchema(BaseModel):
    access_token: str
    refresh_token: str