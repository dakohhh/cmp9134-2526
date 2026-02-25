from pydantic import BaseModel

class RefreshTokenResponseDataSchema(BaseModel):
    access_token: str
    refresh_token: str