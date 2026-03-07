from fastapi import FastAPI
from typing import AsyncGenerator
from settings.config import settings
from contextlib import asynccontextmanager
from sqlmodel import SQLModel, select # noqa: F401
# import web
import asyncio
from app.robot.gateway import robot_telemetry
from app.auth.router import router as auth_router
from fastapi.middleware.cors import CORSMiddleware
from app.database.config import create_db_and_tables # noqa: F401
from app.health.router import router as health_router
from app.map.router import router as map_router
from app.robot.router import router as robot_router
from app.common.handlers import configure_error_middleware
from app.common.utils.process_cors import process_cors_origins

# ws://localhost:5000/ws/telemetry

@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncGenerator[None, None]:
    try:
        # Only should be used in development, most preferred to use alembic to track migrations
        # await create_db_and_tables()
        robot_telemetry_async_task = asyncio.create_task(robot_telemetry())
        yield
        print("Shutting Down Server")
        robot_telemetry_async_task.cancel()
    finally:
        pass


def configure_cors(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=process_cors_origins(settings.CORS_ORIGINS),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def register_routers(app: FastAPI) -> None:
    """Register all application routers/controllers"""
    app.include_router(health_router)
    app.include_router(auth_router)
    app.include_router(map_router)
    app.include_router(robot_router)

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        description="Speech diarization with LLM analysis",
        version=settings.APP_VERSION,
        lifespan=lifespan,
        docs_url=settings.API_DOCS.API_DOCS_URL,
        redoc_url=settings.API_DOCS.API_REDOC_URL,
        openapi_url=settings.API_DOCS.OPENAPI_URL,
        swagger_ui_parameters={"persistAuthorization": True},
    )

    configure_cors(app)
    configure_error_middleware(app)

    register_routers(app)

    return app
