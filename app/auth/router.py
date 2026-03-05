from typing import Annotated

from app.auth.schemas.login_schema import LoginSchema
from app.auth.schemas.register_schema import RegisterSchema
from app.token.schemas.token_schema import TokenSchema
from .state import auth_bearer
from app.user.models import User
from .service import AuthService
from app.common.router import VersionRouter
from app.common.response import HttpResponse
from fastapi import Depends, status as HttpStatus, Cookie, Body
from .schemas.token_refresh_request_schema import TokenRefreshRequestSchema
from .schemas.session_response_data_schema import SessionResponseDataSchema


router = VersionRouter(path="auth", version="1", tags=["Authentication"])


@router.post("/login", response_model=HttpResponse[TokenSchema])
async def login(login_schema: LoginSchema, auth_service: Annotated[AuthService, Depends(AuthService)]) -> HttpResponse[TokenSchema]:
    result = await auth_service.login(login_schema)
    return HttpResponse(message="Login successfully", data=result, status_code=HttpStatus.HTTP_200_OK)

@router.post("/register", response_model=HttpResponse[TokenSchema])
async def register(register_schema: RegisterSchema, auth_service: Annotated[AuthService, Depends(AuthService)]) -> HttpResponse[TokenSchema]:
    result = await auth_service.register(register_schema)
    return HttpResponse(message="Register successfully", data=result, status_code=HttpStatus.HTTP_200_OK)


@router.post("/refresh-token", response_model=HttpResponse[TokenSchema])
async def refresh_token(auth_service: Annotated[AuthService, Depends(AuthService)], refresh_token: Annotated[str | None, Cookie()] = None ) -> HttpResponse[TokenSchema]:
    result = await auth_service.refresh_token(refresh_token)
    return HttpResponse(message="Refresh tokens successfully", data=result, status_code=HttpStatus.HTTP_200_OK)


@router.post("/logout", response_model=HttpResponse[None])
async def logout(
    auth_service: Annotated[AuthService, Depends(AuthService)],
    user: User = Depends(auth_bearer),
    refresh_token: Annotated[str | None, Cookie()] = None 
) -> HttpResponse[None]:
    await auth_service.logout(refresh_token)
    return HttpResponse(message="Logged out successfully", data=None, status_code=HttpStatus.HTTP_200_OK)


@router.get("/session", response_model=HttpResponse[SessionResponseDataSchema])
async def get_user_session(
    auth_service: Annotated[AuthService, Depends(AuthService)],
    user: User = Depends(auth_bearer),
) -> HttpResponse[User]:
    populated_user = await auth_service.get_session(user)
    return HttpResponse(message="User Session", data=populated_user, status_code=HttpStatus.HTTP_200_OK)