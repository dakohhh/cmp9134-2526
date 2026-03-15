import asyncio
from uuid import UUID
from fastapi import WebSocket
from typing import Literal, List
from dataclasses import dataclass
from app.robot.schemas.telemetry_data_schema import TelemetryDataSchema
from app.socket.ws_message import WsMessage, WsMessageType

# Register Channels here (basically module name)
Channel = Literal["robot"]
@dataclass
class Connection():
    user_id: UUID
    websocket: WebSocket

class SocketConnectionManager:
    def __init__(self) -> None:
        self.connections: dict[Channel, List[Connection]] = {}

    async def connect(self, websocket: WebSocket, channel: Channel, user_id: UUID) -> None:
        await websocket.accept()
        if channel not in self.connections:
            self.connections[channel] = []
        self.connections[channel].append(Connection(user_id=user_id, websocket=websocket))

    def disconnect(self, channel: Channel, user_id: UUID) -> None:
        self.connections[channel] = [
            conn for conn in self.connections[channel]
            if conn.user_id != user_id
        ]

    async def broadcast_telemetry_data(self, channel: Channel, data: TelemetryDataSchema) -> None:
        message = WsMessage[TelemetryDataSchema](type=WsMessageType.TELEMETRY, data=data)
        broadcast_tasks = []
        for conn in self.connections.get(channel, []):
            broadcast_tasks.append(conn.websocket.send_json(message.model_dump()))

        await asyncio.gather(*broadcast_tasks)

    async def broadcast_error(self, channel: Channel) -> None:
        message = WsMessage[None](type=WsMessageType.ERROR, data=None)
        broadcast_tasks = []
        for conn in self.connections.get(channel, []):
            broadcast_tasks.append(conn.websocket.send_json(message.model_dump()))

        await asyncio.gather(*broadcast_tasks)



socket_connection_manager = SocketConnectionManager()

