import asyncio
from urllib.parse import urlparse
from settings.config import settings
from websockets.asyncio.client import connect
from app.socket.manager import socket_connection_manager
from app.robot.schemas.telemetry_data_schema import TelemetryDataSchema



def to_websocket_url(url: str) -> str:
    parsed = urlparse(url)
    scheme = "wss" if parsed.scheme == "https" else "ws"
    return parsed._replace(scheme=scheme).geturl()


async def robot_telemetry() -> None:
    while True:
        try:
            async with connect(f"{to_websocket_url(settings.BASE_ROBOT_API_URL)}/ws/telemetry") as websocket:
                while True:
                    message = await websocket.recv()

                    telemetry_data = TelemetryDataSchema.model_validate_json(message)

                    await socket_connection_manager.broadcast_telemetry_data("robot", telemetry_data)

        except Exception as e:
            print(e)
            print("Some Unknown error")
            await socket_connection_manager.broadcast_error("robot")
            await asyncio.sleep(1)

