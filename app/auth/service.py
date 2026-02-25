from fastapi import Depends
from typing import Annotated, Any, Optional
from app.user.models import User
from sqlmodel import select
from settings.config import SettingsDep
from app.user.service import UserService
from app.token.service import TokenService
from app.database.config import DatabaseSession
from app.common.exceptions import UnauthorizedException
from .schemas.token_refresh_request_schema import TokenRefreshRequestSchema

class AuthService:

    def __init__(
            self, 
            settings: SettingsDep,
            session: DatabaseSession,
            user_service: Annotated[UserService, Depends(UserService)],
            token_service: Annotated[TokenService, Depends(TokenService)],
        ):
        self.settings = settings
        self.session = session
        self.user_service = user_service
        self.token_service = token_service
    
    async def refresh_token(self, refresh_token: Optional[str]) -> dict[str, str]:
        if not refresh_token:
            raise UnauthorizedException("invalid or expired token")
    
        tokens = await self.token_service.refresh_token(refresh_token)
        
        return tokens

    async def get_session(self, user: User) -> User:
        populated_user = (await self.session.exec( select(User).where( User.id == user.id ))).one()

        return populated_user




        
