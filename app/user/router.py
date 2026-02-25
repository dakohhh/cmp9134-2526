from uuid import UUID
from .service import UserService
from app.user.models import User
from typing import Annotated, Optional
from app.common.router import VersionRouter
from app.common.response import HttpResponse
from app.auth.state import require_permission
from fastapi import Depends, status as HttpStatus
from app.user.schemas.update_user_schema import UpdateUserSchema
from app.common.paginator import PaginationSchema, PaginatorResult

router = VersionRouter(version="1", path="user", tags=["User"])

@router.get("/", response_model=HttpResponse[PaginatorResult[User]], status_code=HttpStatus.HTTP_200_OK)
async def get_all_users(pagination_schema: Annotated[PaginationSchema, Depends(PaginationSchema)], user_service: Annotated[UserService, Depends(UserService)], user: User = Depends(require_permission()), search: Optional[str]=None) -> HttpResponse[PaginatorResult[User]]:
    result = await user_service.get_all_users(pagination_schema, search)
    return HttpResponse(message="Get all Users", data=result, status_code=HttpStatus.HTTP_200_OK)


@router.get("/{user_id}", response_model=HttpResponse[User], status_code=HttpStatus.HTTP_200_OK)
async def get_user(user_id: UUID, user_service: Annotated[UserService, Depends(UserService)], user: User = Depends(require_permission())) -> HttpResponse[User]:
    result = await user_service.get_user(user_id)
    return HttpResponse(message="Get user", data=result, status_code=HttpStatus.HTTP_200_OK)


@router.patch("/{user_id}", response_model=HttpResponse[User], status_code=HttpStatus.HTTP_200_OK)
async def update_user(user_id: UUID, update_user_schema: UpdateUserSchema, user_service: Annotated[UserService, Depends(UserService)], user: User = Depends(require_permission())) -> HttpResponse[User]:
    result = await user_service.update_user(user_id, update_user_schema)
    return HttpResponse(message="Update user", data=result, status_code=HttpStatus.HTTP_200_OK)


@router.delete("/{user_id}", response_model=HttpResponse[None], status_code=HttpStatus.HTTP_200_OK)
async def delete_user(user_id: UUID, user_service: Annotated[UserService, Depends(UserService)], user: User = Depends(require_permission())) -> HttpResponse[None]:
    await user_service.delete_user(user, user_id)
    return HttpResponse(message="Delete user", data=None, status_code=HttpStatus.HTTP_200_OK)





