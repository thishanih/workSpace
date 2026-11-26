import certifi
from pymongo import MongoClient
from pymongo.database import Database
from starlette.requests import Request

from app.core.config import settings


def create_mongo_client() -> MongoClient:
    return MongoClient(
        settings.mongo_uri,
        tlsCAFile=certifi.where(),
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
    )


def initialize_indexes(database: Database) -> None:
    database["users"].create_index("email", unique=True)
    database["refresh_tokens"].create_index("expires_at", expireAfterSeconds=0)
    database["todos"].create_index([("owner_id", 1), ("created_at", -1)])
    database["comments"].create_index([("todo_id", 1), ("created_at", -1)])
    database["activities"].create_index([("owner_id", 1), ("created_at", -1)])


def get_database(request: Request) -> Database:
    database = request.app.state.mongo_client[settings.mongo_database]
    if not request.app.state.indexes_initialized:
        with request.app.state.index_lock:
            if not request.app.state.indexes_initialized:
                initialize_indexes(database)
                request.app.state.indexes_initialized = True
    return database
