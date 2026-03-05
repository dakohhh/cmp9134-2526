from websockets.asyncio.client import connect

async def robot_telemetry () -> None:
    async with connect("ws://localhost:5555/ws/telemetry") as websocket:
        message = await websocket.recv()

        print(message)
