from pydantic_settings import BaseSettings, SettingsConfigDict
from src.common.config import settings as global_settings

class Settings(BaseSettings):
    PROJECT_NAME: str = "SIE Ingestion API"
    API_V1_STR: str = "/api/v1"
    
    HOST: str = global_settings.api.HOST
    PORT: int = global_settings.api.PORT
    GRPC_PORT: int = global_settings.api.GRPC_PORT
    API_KEY: str = global_settings.api.KEY
    CORS_ORIGINS: list[str] = global_settings.api.CORS_ORIGINS

    model_config = SettingsConfigDict(env_prefix="API_", env_file=".env", extra="ignore")

settings = Settings()
