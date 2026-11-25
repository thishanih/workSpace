from fastapi import APIRouter

from app.modules.activities.router import router as activities_router
from app.modules.auth.router import router as auth_router
from app.modules.comments.router import router as comments_router
from app.modules.health.router import router as health_router
from app.modules.todos.router import router as todos_router
from app.modules.users.router import router as users_router

api_router = APIRouter()
api_router.include_router(health_router)
api_router.include_router(auth_router)
api_router.include_router(users_router)
api_router.include_router(todos_router)
api_router.include_router(comments_router)
api_router.include_router(activities_router)
