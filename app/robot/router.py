from uuid import uuid4
from typing import Annotated
from app.user.models import User
from app.auth.state import auth_bearer
from .service import RobotService
from fastapi import Depends, status as HttpStatus
from app.common.response import HttpResponse
from app.common.router import VersionRouter
from fastapi import WebSocket, WebSocketDisconnect
from .schemas.move_robot_request_schema import MoveRobotRequestSchema
from app.socket.manager import socket_connection_manager

router = VersionRouter(path="robot", version="1", tags=["Robot"])


@router.post("/move/", response_model=HttpResponse[None], status_code=HttpStatus.HTTP_200_OK)
async def move_robot(move_robot_request_schema: MoveRobotRequestSchema, robot_service: Annotated[RobotService, Depends(RobotService)], user: User = Depends(auth_bearer)) -> HttpResponse[None]:
    await robot_service.move_robot(user, move_robot_request_schema)
    
    return HttpResponse(message="Move Robot", data=None, status_code=HttpStatus.HTTP_200_OK)


@router.post("/reset/", response_model=HttpResponse[None], status_code=HttpStatus.HTTP_200_OK)
async def reset_robot(robot_service: Annotated[RobotService, Depends(RobotService)], user: User = Depends(auth_bearer)) -> HttpResponse[None]:
    await robot_service.reset_robot(user)

    return HttpResponse(message="Reset Robot", data=None, status_code=HttpStatus.HTTP_200_OK)

@router.websocket("/")
async def robot_ws(websocket: WebSocket) -> None:
    connection_id = uuid4()
    await socket_connection_manager.connect(websocket, "robot", connection_id)
    try:
        while True:  # Keep connection alive — broadcasting is handled by the socket manager
            await websocket.receive_text()
    except WebSocketDisconnect:
        socket_connection_manager.disconnect("robot", connection_id)
