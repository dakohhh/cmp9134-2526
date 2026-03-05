import os
import certifi
from pathlib import Path
from fastapi import Depends
from pydantic import Field
from dotenv import load_dotenv
from functools import lru_cache
from datetime import timedelta
from pydantic_settings import BaseSettings
from typing import Annotated, Literal, cast

load_dotenv()

EnvironmentType = Literal["development", "production"]
env = os.getenv("PYTHON_ENV", "development")
PYTHON_ENV: EnvironmentType = cast(EnvironmentType, env)

# Core application paths
_BASE_DIR: Path = Path(__file__).resolve().parent.parent
BASE_DIR: Path = _BASE_DIR
CERTIFICATE: str = os.path.join(os.path.dirname(certifi.__file__), "cacert.pem")
DOTENV: str = os.path.join(_BASE_DIR, ".env")


class APIDocsConfig(BaseSettings):
    """API Documentation configurations."""

    API_DOCS_USERNAME: str = Field("admin", env="API_DOCS_USERNAME")  # type: ignore
    API_DOCS_PASSWORD: str = Field("password", env="API_DOCS_PASSWORD")  # type: ignore
    API_DOCS_URL: str = Field("/docs", env="API_DOCS_URL")  # type: ignore
    API_REDOC_URL: str = Field("/redoc", env="API_REDOC_URL")  # type: ignore
    OPENAPI_URL: str = Field("/openapi.json", env="OPENAPI_URL")  # type: ignore


class MailerConfig(BaseSettings):
    """Mail/SMTP configuration for MailService."""

    MAILER_SMTP_HOST: str = Field("smtp.gmail.com", env="MAILER_SMTP_HOST")  # type: ignore
    MAILER_SMTP_PORT: int = Field(587, env="MAILER_SMTP_PORT")  # type: ignore
    MAILER_SMTP_USER: str = Field("", env="MAILER_SMTP_USER")  # type: ignore
    MAILER_SMTP_PASSWORD: str = Field("", env="MAILER_SMTP_PASSWORD")  # type: ignore
    MAILER_SECURE: bool = Field(False, env="MAILER_SECURE")  # type: ignore
    MAILER_FROM_EMAIL: str = Field("", env="MAILER_FROM_EMAIL")  # type: ignore
    MAILER_FROM_NAME: str = Field("FreudWriter", env="MAILER_FROM_NAME")  # type: ignore


class GlobalConfig(BaseSettings):
    """Base configuration class with shared settings across environments."""

    APP_NAME: str ="cmp9134-2526-backend"
    APP_ISS: str = "cmp9134-2526-backend"
    APP_VERSION: str = "0.0.1"
    APPLICATION_CERTIFICATE: str = Field(default=CERTIFICATE)
    BASE_DIR: Path = Field(default=_BASE_DIR)

    ENVIRONMENT: EnvironmentType = PYTHON_ENV

    BCRYPT_SALT: int = 10

    JWT_ALGORITHM: str = Field("HS256")
    
    JWT_SECRET_KEY: str = Field(..., description="WARNING: Use strong secret in production")

    ROTATE_REFRESH_TOKEN: bool = True
    ACCESS_TOKEN_JWT_EXPIRES_IN: timedelta = timedelta(hours=1)
    REFRESH_TOKEN_JWT_EXPIRES_IN: timedelta = timedelta(days=7)


    # Configs
    API_DOCS: APIDocsConfig = Field(default_factory=APIDocsConfig)  # type: ignore

    DATABASE_URL: str = Field(..., env="DATABASE_URL")  # type: ignore
    # Redis
    REDIS_URL: str = Field(..., env="REDIS_URL")  # type: ignore


    # CORS
    CORS_ORIGINS: str = Field("*", env="CORS_ORIGINS")  # type: ignore

    BASE_ROBOT_API_URL: str = Field(..., env="BASE_ROBOT_API_URL") # type: ignore
    
   


ConfigType = GlobalConfig

@lru_cache()
def get_settings() -> ConfigType:
    """Factory function to get environment-specific settings."""
    configs = {
        "development": GlobalConfig,
        "production": GlobalConfig,
    }
    if not PYTHON_ENV or PYTHON_ENV not in configs:
        raise ValueError(
            f"Invalid deployment environment: `{env}`. Must be one of: {list(configs.keys())}"
        )
    return configs[PYTHON_ENV]()  # type: ignore


settings = get_settings()
SettingsDep = Annotated[ConfigType, Depends(get_settings)]
