from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.security import decode_access_token

_PUBLIC_PATHS = {
    "/api/health",
    "/api/auth/register",
    "/api/auth/login",
    "/api/auth/refresh",
}


class AuthenticationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        path = request.url.path
        authorization = request.headers.get("authorization")
        if not path.startswith("/api/") or path in _PUBLIC_PATHS or not authorization:
            return await call_next(request)

        scheme, separator, token = authorization.partition(" ")
        if scheme.lower() != "bearer" or not separator or not token:
            return JSONResponse(
                status_code=401,
                content={"detail": "A valid bearer token is required."},
                headers={"WWW-Authenticate": "Bearer"},
            )

        user_id = decode_access_token(token)
        if user_id is None:
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid or expired bearer token."},
                headers={"WWW-Authenticate": "Bearer"},
            )

        request.state.user_id = user_id
        return await call_next(request)
