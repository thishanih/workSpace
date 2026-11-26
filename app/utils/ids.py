from bson import ObjectId

from app.core.exceptions import AppError


def parse_object_id(value: str, resource_name: str) -> ObjectId:
    if not ObjectId.is_valid(value):
        raise AppError(404, f"{resource_name} not found.")
    return ObjectId(value)
