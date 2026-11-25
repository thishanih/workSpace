from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from threading import Lock

from fastapi import FastAPI

from app.core.config import settings
from app.core.database import create_mongo_client
from app.middleware.auth import AuthenticationMiddleware
from app.middleware.error_handler import register_exception_handlers
from app.middleware.rate_limit import RateLimitMiddleware
from app.routers.api import api_router


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    application.state.mongo_client = create_mongo_client()
    application.state.indexes_initialized = False
    application.state.index_lock = Lock()
    try:
        yield
    finally:
        application.state.mongo_client.close()


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.include_router(api_router, prefix="/api")
register_exception_handlers(app)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(AuthenticationMiddleware)
