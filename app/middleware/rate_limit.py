import asyncio
import time
from collections.abc import Callable

from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.config import settings

_AUTH_PATHS = {"/api/auth/register", "/api/auth/login"}


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: Callable) -> None:
        super().__init__(app)
        self._requests: dict[tuple[str, str], tuple[int, float]] = {}
        self._lock = asyncio.Lock()

    async def dispatch(self, request: Request, call_next) -> Response:
        if not request.url.path.startswith("/api/"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        route_group = "auth" if request.url.path in _AUTH_PATHS else "api"
        key = (client_ip, route_group)
        now = time.monotonic()
        limit = (
            settings.auth_rate_limit_requests
            if route_group == "auth"
            else settings.rate_limit_requests
        )

        async with self._lock:
            count, reset_at = self._requests.get(
                key, (0, now + settings.rate_limit_window_seconds)
            )
            if now >= reset_at:
                count, reset_at = 0, now + settings.rate_limit_window_seconds
            if count >= limit:
                retry_after = max(1, int(reset_at - now))
                return JSONResponse(
                    status_code=429,
                    content={"detail": "Too many requests. Try again later."},
                    headers={"Retry-After": str(retry_after)},
                )
            self._requests[key] = (count + 1, reset_at)

            if len(self._requests) > 10_000:
                self._requests = {
                    item_key: item
                    for item_key, item in self._requests.items()
                    if item[1] > now
                }

        return await call_next(request)
