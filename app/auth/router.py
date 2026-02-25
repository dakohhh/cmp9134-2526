from typing import Annotated
from .state import auth_bearer
from app.user.models import User
from .service import AuthService
from app.common.router import VersionRouter
from app.common.response import HttpResponse
from fastapi import Depends, status as HttpStatus, Cookie
from .schemas.token_refresh_request_schema import TokenRefreshRequestSchema
from .schemas.session_response_data_schema import SessionResponseDataSchema
from .schemas.refresh_token_response_data_schema import RefreshTokenResponseDataSchema


router = VersionRouter(path="auth", version="1", tags=["Authentication"])


# @router.post("/login", response_model=HttpResponse[LoginResponseDataSchema])
# async def login(login_schema: LoginSchema, auth_service: Annotated[AuthService, Depends(AuthService)]) -> HttpResponse[LoginResponseDataSchema]:
#     result = await auth_service.login(login_schema)
#     return HttpResponse(message="Login successfully", data=result, status_code=HttpStatus.HTTP_200_OK) # type: ignore


@router.post("/refresh-token", response_model=HttpResponse[RefreshTokenResponseDataSchema])
async def refresh_token(auth_service: Annotated[AuthService, Depends(AuthService)], refresh_token: Annotated[str | None, Cookie()] = None ) -> HttpResponse[RefreshTokenResponseDataSchema]:
    result = await auth_service.refresh_token(refresh_token)
    return HttpResponse(message="Refresh tokens successfully", data=result, status_code=HttpStatus.HTTP_200_OK) # type: ignore


@router.get("/session", response_model=HttpResponse[SessionResponseDataSchema])
async def get_user_session(
    auth_service: Annotated[AuthService, Depends(AuthService)],
    user: User = Depends(auth_bearer),
) -> HttpResponse[User]:
    populated_user = await auth_service.get_session(user)
    return HttpResponse(message="User Session", data=populated_user, status_code=HttpStatus.HTTP_200_OK) # type: ignore