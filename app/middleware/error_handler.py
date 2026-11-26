import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pymongo.errors import PyMongoError

from app.core.exceptions import AppError

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, error: AppError) -> JSONResponse:
        return JSONResponse(
            status_code=error.status_code,
            content={"detail": error.detail},
        )

    @app.exception_handler(PyMongoError)
    async def handle_database_error(
        request: Request,
        error: PyMongoError,
    ) -> JSONResponse:
        logger.error(
            "MongoDB operation failed",
            exc_info=(type(error), error, error.__traceback__),
        )
        return JSONResponse(
            status_code=503,
            content={"detail": "The database is temporarily unavailable."},
        )
