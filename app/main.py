from fastapi import FastAPI

from app.routers.api import api_router

app = FastAPI(title="Todo API")
app.include_router(api_router, prefix="/api")
