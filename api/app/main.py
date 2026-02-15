from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.api.v1.api import api_router
from app.core.config import settings
from app.core.exception_handlers import register_exception_handlers
from app.core.logging import LoggerConfig
from app.core.middleware import LoggingMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    Path("logs").mkdir(exist_ok=True)
    LoggerConfig.setup()
    logger.info(f"🚀 Starting {settings.PROJECT_NAME}")
    logger.info(f"📍 Environment: {settings.ENVIRONMENT}")
    logger.info(f"🌐 API Prefix: {settings.API_V1_STR}")
    yield
    logger.info(f"🛑 Shutting down {settings.PROJECT_NAME}")


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

register_exception_handlers(app)

app.add_middleware(LoggingMiddleware)

if settings.FRONTEND_URL:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(settings.FRONTEND_URL)],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.info(f"✅ CORS enabled for: {settings.FRONTEND_URL}")

app.include_router(api_router, prefix=settings.API_V1_STR)


@app.get("/health")
async def health_check():
    return {"status": "ok", "project": settings.PROJECT_NAME}
