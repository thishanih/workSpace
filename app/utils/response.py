from typing import Any

from bson import ObjectId
from fastapi.encoders import jsonable_encoder


def serialize_document(document: dict[str, Any]) -> dict[str, Any]:
    serialized = dict(document)
    identifier = serialized.pop("_id", None)
    if identifier is not None:
        serialized["id"] = str(identifier)
    return jsonable_encoder(serialized, custom_encoder={ObjectId: str})
