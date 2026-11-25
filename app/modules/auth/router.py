from fastapi import APIRouter, Depends, status
from pymongo.database import Database

from app.dependencies.database import get_database
from app.modules.auth.controller import login, register
from app.modules.auth.schemas import LoginRequest, RegisterRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_endpoint(
    payload: RegisterRequest,
    database: Database = Depends(get_database),
) -> TokenResponse:
    return register(database, payload)


@router.post("/login", response_model=TokenResponse)
def login_endpoint(
    payload: LoginRequest,
    database: Database = Depends(get_database),
) -> TokenResponse:
    return login(database, payload)
