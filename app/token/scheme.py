from enum import Enum
from calendar import timegm
from pydantic import BaseModel, Field, ConfigDict, field_serializer
from typing import Optional, Any, Set, Any
from fastapi import Request,Depends
from datetime import datetime, timedelta, timezone
from fastapi.security import HTTPBearer
from .exception  import TokenError
from  .dependency import get_token_backend
from .backends import TokenBackend 
from  .tokens import TokenType, Token

class JwtHTTPBearer(HTTPBearer):

    async def __call__(self, request: Request, token_backend: TokenBackend = Depends(get_token_backend)) -> Token: # type: ignore
        data = await super().__call__(request)

        if not data:
            raise Exception()

        token = token_backend.decode_token(data.credentials)

        if token.type == TokenType.REFRESH:
            raise TokenError("Refresh token is not allowed to access the protected resources")

        return token