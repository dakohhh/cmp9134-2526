import bcrypt
from fastapi import Depends
from sqlmodel import select
from datetime import datetime, timezone
from app.audit_log.models import ActionEnum
from app.audit_log.schemas.create_audit_log_schema import CreateAuditLogSchema
from app.audit_log.service import AuditLogService
from app.auth.schemas.login_schema import LoginSchema
from app.user.models import User
from settings.config import SettingsDep
from app.user.service import UserService
from app.token.service import TokenService
from typing import Annotated, Optional
from app.database.config import DatabaseSession
from .schemas.register_schema import RegisterSchema
from app.token.schemas.token_schema import TokenSchema
from app.common.exceptions import UnauthorizedException, BadRequestException
from .schemas.token_refresh_request_schema import TokenRefreshRequestSchema

class AuthService:

    def __init__(
            self, 
            settings: SettingsDep,
            session: DatabaseSession,
            user_service: Annotated[UserService, Depends(UserService)],
            token_service: Annotated[TokenService, Depends(TokenService)],
            audit_log_service: Annotated[AuditLogService, Depends(AuditLogService)]
        ):
        self.settings = settings
        self.session = session
        self.user_service = user_service
        self.token_service = token_service
        self.audit_log_service = audit_log_service
    
    async def refresh_token(self, refresh_token: Optional[str]) -> TokenSchema:
        if not refresh_token:
            raise UnauthorizedException("invalid or expired token")
    
        tokens = await self.token_service.refresh_token(refresh_token)
        
        return tokens
    

    async def login(self, login_schema: LoginSchema) -> TokenSchema:

        existing_user = (await self.session.exec( select(User).where( User.email == login_schema.email ))).first()

        if not existing_user:
            raise BadRequestException("incorrect email or password")
        
        is_password_valid = bcrypt.checkpw(password=login_schema.password.encode(), hashed_password=existing_user.password.encode())

        if not is_password_valid:
            raise UnauthorizedException("Incorrect email or password")
        
        tokens = await self.token_service.generate_auth_token(existing_user.id)

        # Update the last login info
        existing_user.last_login = datetime.now(timezone.utc)

        await self.session.commit()

        await self.session.refresh(existing_user)

        await self.audit_log_service.create_audit_log(
            existing_user, 
            CreateAuditLogSchema(
                action=ActionEnum.LOGIN, 
                navigation_direction=None,
            )
        )
        
        return tokens
    
    async def register(self, register_schema: RegisterSchema) -> TokenSchema:

        # Check if email is taken
        existing_user = (await self.session.exec( select(User).where( User.email == register_schema.email ))).first()

        if existing_user:
            raise BadRequestException("Email already taken")
        
        hashed_password = bcrypt.hashpw(password=register_schema.password.encode(), salt=bcrypt.gensalt()).decode()

        new_user = User(full_name=register_schema.full_name,  password=hashed_password, email=register_schema.email, is_super_admin=False, is_active=True)

        self.session.add(new_user)

        await self.session.commit()

        await self.session.refresh(new_user)

        tokens = await self.token_service.generate_auth_token(new_user.id)

        return tokens

    async def logout(self, refresh_token: Optional[str]) -> None:
        if refresh_token:
            await self.token_service.revoke_refresh_token(refresh_token)

    async def get_session(self, user: User) -> User:
        populated_user = (await self.session.exec( select(User).where( User.id == user.id ))).one()

        return populated_user




        
