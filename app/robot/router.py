from uuid import UUID
from typing import Annotated
from app.user.models import User
from app.common.router import VersionRouter
from app.common.response import HttpResponse
from fastapi import WebSocket, WebSocketDisconnect
from fastapi import Depends, status as HttpStatus
from app.auth.state import require_permission
from app.socket.manager import SocketConnectionManager
from app.admin.schemas.update_user_role_schema import UpdateUserRoleSchema


router = VersionRouter(path="robot", version="1", tags=["Robot"])

@router.websocket("/")
async def test(websocket: WebSocket, socket_connection_manager: Annotated[SocketConnectionManager, Depends(SocketConnectionManager)]) -> None:
    await socket_connection_manager.connect(websocket)
    try:
        # socket_connection_manager
    except WebSocketDisconnect:
        socket_connection_manager.disconnect(websocket)
