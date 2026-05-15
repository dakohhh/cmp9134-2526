from typing import Annotated
from uuid import UUID
from app.user.models import User
from .service import AdminService
from app.common.router import VersionRouter
from app.common.response import HttpResponse
from fastapi import Depends, status as HttpStatus
from app.auth.state import require_permission
from app.common.paginator import PaginationSchema, PaginatorResult
from app.admin.schemas.update_user_role_schema import UpdateUserRoleSchema
from app.admin.schemas.get_all_users_response_schema import GetAllUsersResponseSchema


router = VersionRouter(path="admin", version="1", tags=["Admin"])


@router.get("/users/", response_model=HttpResponse[GetAllUsersResponseSchema])
async def get_all_users(
    paginator_schema: Annotated[PaginationSchema, Depends(PaginationSchema)],
    admin_service: Annotated[AdminService, Depends(AdminService)],
    _: User = Depends(require_permission()),
) -> HttpResponse[PaginatorResult[User]]:
    results = await admin_service.get_all_users(paginator_schema)
    return HttpResponse(message="Get all Users", data=results, status_code=HttpStatus.HTTP_200_OK)


@router.post("/user/{user_id}/role", response_model=HttpResponse[None])
async def update_user_role(user_id: UUID, update_user_role_schema: UpdateUserRoleSchema, auth_service: Annotated[AdminService, Depends(AdminService)], user: User = Depends(require_permission())) -> HttpResponse[None]:
    await auth_service.update_user_role(user_id, update_user_role_schema, user)
    return HttpResponse(message="Update User Role", data=None, status_code=HttpStatus.HTTP_200_OK)