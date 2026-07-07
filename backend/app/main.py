from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.analytics import router as analytics_router
from app.api.v1.auth import router as auth_router
from app.api.v1.categories import router as categories_router
from app.api.v1.collections import router as collections_router
from app.api.v1.constellation import router as constellation_router
from app.api.v1.feedback import router as feedback_router
from app.api.v1.health import router as health_router
from app.api.v1.items import router as items_router
from app.api.v1.search import router as search_router
from app.core.config import get_settings
from app.core.errors import AppError, app_error_handler
from app.core.logging import configure_logging
from app.core.middleware import RequestContextMiddleware

settings = get_settings()
configure_logging()

app = FastAPI(
    title="MemoryLens API",
    version="0.1.0",
    description="Find things you partially remember.",
)

app.add_middleware(RequestContextMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(AppError, app_error_handler)

app.include_router(health_router, prefix="/api/v1", tags=["health"])
app.include_router(auth_router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(categories_router, prefix="/api/v1", tags=["categories"])
app.include_router(search_router, prefix="/api/v1", tags=["search"])
app.include_router(items_router, prefix="/api/v1", tags=["items"])
app.include_router(collections_router, prefix="/api/v1", tags=["collections"])
app.include_router(feedback_router, prefix="/api/v1", tags=["feedback"])
app.include_router(analytics_router, prefix="/api/v1", tags=["analytics"])
app.include_router(constellation_router, prefix="/api/v1", tags=["constellation"])
