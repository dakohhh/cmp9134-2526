from uuid import UUID
from typing import Callable
from sqlmodel import select
from app.user.models import User
from fastapi import Depends, Request
from app.token.scheme import JwtHTTPBearer
from app.database.config import DatabaseSession
from app.token.backends import get_token_backend, TokenBackend
from app.common.exceptions import UnauthorizedException, ForbiddenException


class AuthJwtHTTPBearer(JwtHTTPBearer):
    async def __call__(self, request: Request, session: DatabaseSession,  token_backend: TokenBackend = Depends(get_token_backend)) -> User: # type: ignore
        token = await super().__call__(request, token_backend)

        user = (await session.exec(select(User).where(User.id == UUID(token.sub)))).first()

        if not user or not user.is_active:
            raise UnauthorizedException("Invalid token")
        
        request.scope["user"] = user
        
        return user
    
auth_bearer = AuthJwtHTTPBearer()


def require_permission() -> Callable[[User], User]:
    def guard(user: User = Depends(auth_bearer)) -> User:
        if not user.is_super_admin:
            raise ForbiddenException("Forbidden")
        return user
    return guard