import httpx
from fastapi import FastAPI
from typing import AsyncGenerator
from settings.config import settings
from contextlib import asynccontextmanager
from sqlmodel import SQLModel, select # noqa: F401
import asyncio
from app.robot.gateway import robot_telemetry
from redis.asyncio import from_url as redis_from_url
from app.auth.router import router as auth_router
from fastapi.middleware.cors import CORSMiddleware
from app.database.config import create_db_and_tables # noqa: F401
from app.health.router import router as health_router
from app.map.router import router as map_router
from app.robot.router import router as robot_router
from app.audit_log.router import router as audit_log_router
from app.admin.router import router as admin_router
from app.common.handlers import configure_error_middleware
from app.common.utils.process_cors import process_cors_origins

@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncGenerator[None, None]:
    try:
        # Only should be used in development, most preferred to use alembic to track migrations
        # await create_db_and_tables()
        async with httpx.AsyncClient(
            limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
            timeout=30.0,
        ) as http_async_client:

            redis_client = redis_from_url(settings.REDIS_URL, decode_responses=True)
            
            #Ping the redis client to open the TCP connection
            await redis_client.ping() # type: ignore

            robot_telemetry_async_task = asyncio.create_task(robot_telemetry())


            application.state.http_async_client = http_async_client

            application.state.redis_client = redis_client

            yield
            robot_telemetry_async_task.cancel()
            await redis_client.aclose()
    finally:
        print("Shutting Down Server")

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
    app.include_router(audit_log_router)
    app.include_router(admin_router)

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        description="ROBOT BACKEND cmp9134-2526",
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
