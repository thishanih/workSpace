from collections.abc import Callable
from typing import Any, TypeVar

from pymongo import DESCENDING
from pymongo.collection import Collection

T = TypeVar("T")


def paginate_collection(
    collection: Collection,
    query: dict[str, Any],
    page: int,
    page_size: int,
    mapper: Callable[[dict[str, Any]], T],
) -> dict[str, Any]:
    offset = (page - 1) * page_size
    documents = (
        collection.find(query)
        .sort("created_at", DESCENDING)
        .skip(offset)
        .limit(page_size)
    )
    return {
        "items": [mapper(document) for document in documents],
        "page": page,
        "page_size": page_size,
        "total": collection.count_documents(query),
    }
