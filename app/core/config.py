import logging

from pydantic import model_validator
from pydantic_settings import SettingsConfigDict
from video_enrichment_orm.core.config import Settings as ORMSettings

logger = logging.getLogger("uvicorn")


class Settings(ORMSettings):
    model_config = SettingsConfigDict(env_file=".env")

    # Environment configuration
    ENVIRONMENT: str
    TESTING: bool

    # API configuration
    PROJECT_NAME: str = "video-enrichment-api"
    API_V1_STR: str = "/video-enrichment-api/v1"
    API_VERSION: str = "0.1.0"

    AUTH_HEADER_KEY: str = ""
    AUTH_SECRET_KEY: str = ""

    # CORS configuration
    CORS_ORIGINS: list[str] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ["*"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]

    # S3 configuration
    S3_PROFILE: str = ""
    S3_BUCKET: str = ""
    S3_BASE_PATH: str = ""
    S3_GALLERY_PATH: str = "gallery"
    S3_VIDEO_PATH: str = "videos"

    @model_validator(mode="after")
    def ensemble_s3_paths(self):
        self.S3_BASE_PATH = f"{self.S3_BUCKET}/{self.S3_BASE_PATH}"
        self.S3_GALLERY_PATH = f"{self.S3_BASE_PATH}/{self.S3_GALLERY_PATH}"
        self.S3_VIDEO_PATH = f"{self.S3_BASE_PATH}/{self.S3_VIDEO_PATH}"
        return self


settings = Settings()
