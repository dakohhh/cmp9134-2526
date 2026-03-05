from typing import Annotated
from uuid import UUID
from app.user.models import User
from .service import AdminService
from app.common.router import VersionRouter
from app.common.response import HttpResponse
from fastapi import Depends, status as HttpStatus
from app.auth.state import require_permission
from app.admin.schemas.update_user_role_schema import UpdateUserRoleSchema


router = VersionRouter(path="admin", version="1", tags=["Admin"])


@router.post("/user/{user_id}/role", response_model=HttpResponse[None])
async def update_user_role(user_id: UUID, update_user_role_schema: UpdateUserRoleSchema, auth_service: Annotated[AdminService, Depends(AdminService)], user: User=Depends(require_permission)) -> HttpResponse[None]:
    await auth_service.update_user_role(user_id, update_user_role_schema)
    return HttpResponse(message="Update User Role", data=None, status_code=HttpStatus.HTTP_200_OK) # type: ignore