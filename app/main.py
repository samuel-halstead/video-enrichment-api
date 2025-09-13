from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.endpoints import (
    detection,
    entity,
    entity_media_gallery,
    healthcheck,
    segment_detection,
    taxonomy,
    video,
)
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

app.include_router(healthcheck.router, prefix=settings.API_V1_STR)
app.include_router(video.router, prefix=settings.API_V1_STR)
app.include_router(taxonomy.router, prefix=settings.API_V1_STR)
app.include_router(entity.router, prefix=settings.API_V1_STR)
app.include_router(entity_media_gallery.router, prefix=settings.API_V1_STR)
app.include_router(segment_detection.router, prefix=settings.API_V1_STR)
app.include_router(detection.router, prefix=settings.API_V1_STR)
