from enum import Enum
from .exception  import TokenError
from typing import Optional, Any, Set
from datetime import datetime, timedelta
from  .utils import get_current_time, datetime_to_epoch
from pydantic import BaseModel, Field, ConfigDict, field_serializer


class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"


class Token(BaseModel):
    sub: str # The user id
    type: TokenType
    exp: Optional[datetime] = Field(default=None) # The expiration time
    iat: Optional[datetime] = Field(default=None) # The issue time
    iss: Optional[str] = Field(default="default") # The name of your app
    jti: Optional[str] = Field(default=None) # Unique identifier of the Refresh token for blacklisting and rotating


    model_config = ConfigDict(use_enum_values=True, extra="allow")

    def __init__(self, **kwargs: dict[str, Any]) -> None:
        super().__init__(**kwargs)
        if not self.verify_exp():
            raise TokenError("Token has expired")
        if not self.verify_type(self.type):
            raise TokenError("Token type is invalid")

    def verify_exp(self) -> bool:
        if self.exp is None:
            return True
        return self.exp > get_current_time()
    
    def verify_type(self, expected_type: TokenType) -> bool:
        if self.type == expected_type:
            return True
        return False
    
    @field_serializer("exp", "iat")
    def serialize_datetime(self, value: datetime, info: Any)-> int:
        return datetime_to_epoch(value)
    


class AccessToken(Token):
    """
    The access token is used to access the protected resources.
    """
    type: TokenType = Field(default=TokenType.ACCESS)

class RefreshToken(Token):
    """
    The refresh token is used to refresh the access token.
    """

    type: TokenType = Field(default=TokenType.REFRESH)

    @property
    def no_copy_claims(self) -> Set[str]:
        # The claims to not copy from refresh token
        return {"exp", "iat", "type"} 

    def get_access_token(
    self,
    *,
    issue_time: Optional[datetime] = None, 
    expires_in: Optional[timedelta] = None, 
    jti: Optional[str] = None
    ) -> AccessToken:
        now = issue_time or get_current_time()
        expires_in = expires_in or timedelta(minutes=15)

        access_claims = {
            "sub": self.sub,
            "exp": now + expires_in,
            "iat": now,
            "type": TokenType.ACCESS,
            "jti": jti or self.jti
        }

        for claim, value in self.model_dump().items():
            if claim in self.no_copy_claims or claim in access_claims:
                continue
            access_claims[claim] = value

        return AccessToken(**access_claims) # type: ignore
