from uuid import UUID, uuid4
from fastapi import Depends
from sqlmodel import select
from app.token.schemas.token_schema import TokenSchema
from .tokens import RefreshToken
from app.user.models import User
from .utils import get_current_time
from settings.config import SettingsDep
from datetime import datetime, timezone
from app.database.config import DatabaseSession
from app.common.exceptions import UnauthorizedException
from .models import RefreshToken as RefreshTokenMOdel
from .backends import TokenBackend, get_token_backend

class TokenService:
    def __init__(self, session: DatabaseSession, settings: SettingsDep, token_backend: TokenBackend = Depends(get_token_backend)):
        self.session = session
        self.settings = settings
        self.token_backend = token_backend


    async def generate_auth_token(self, user_id: UUID) -> TokenSchema:

        current_time = get_current_time()

        refresh_token = RefreshToken(
            sub=str(user_id),
            iss=self.settings.APP_ISS,
            iat=current_time,
            exp=current_time + self.settings.REFRESH_TOKEN_JWT_EXPIRES_IN,
            jti=str(uuid4())
        )

        access_token = refresh_token.get_access_token(issue_time=current_time, expires_in=self.settings.ACCESS_TOKEN_JWT_EXPIRES_IN, jti=str(uuid4()))

        tokens = TokenSchema(
            access_token=self.token_backend.encode_token(access_token),
            refresh_token=self.token_backend.encode_token(refresh_token)
        )


        assert refresh_token.exp is not None, "Refresh token must have an expiry"

        new_refresh_token_model = RefreshTokenMOdel(
            token=tokens.refresh_token,
            expires_at=refresh_token.exp,
            user_id=user_id
        )

        self.session.add(new_refresh_token_model)


        await self.session.commit()
        
        return tokens
    

    async def revoke_refresh_token(self, refresh_token: str) -> None:
        token = (await self.session.exec(
            select(RefreshTokenMOdel).where(RefreshTokenMOdel.token == refresh_token)
        )).first()

        if token and not token.is_blacklisted:
            token.is_blacklisted = True
            await self.session.commit()

    async def refresh_token(self, refresh_token: str) -> TokenSchema:

        payload = self.token_backend.decode_token(token=refresh_token)

        user = (await self.session.exec(select(User).where( User.id == UUID(payload.sub) ))).first()

        if not user:
            raise UnauthorizedException("invalid or expired token")
        
        user_id = user.id

        token = (await self.session.exec(select(RefreshTokenMOdel).where( RefreshTokenMOdel.token == refresh_token ))).first()

        if not token:
            raise UnauthorizedException("invalid or expired token")
        
        if token.is_blacklisted:
            raise UnauthorizedException("Refresh token revoked")
        
        # Check expired token
        if token.expires_at < datetime.now(timezone.utc):
            raise UnauthorizedException("invalid or expired token")
        
        if self.settings.ROTATE_REFRESH_TOKEN:
            token.is_blacklisted = True
            await self.session.commit()
    

        tokens = await self.generate_auth_token(user_id)

        return tokens
