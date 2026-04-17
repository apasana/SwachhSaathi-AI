from __future__ import annotations

from functools import lru_cache

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import ServerSelectionTimeoutError

from utils.config import settings


class MongoConnectionError(RuntimeError):
    pass


@lru_cache(maxsize=1)
def get_client() -> MongoClient:
    client = MongoClient(settings.MONGO_URI, serverSelectionTimeoutMS=3000)
    try:
        client.admin.command("ping")
    except ServerSelectionTimeoutError as exc:
        raise MongoConnectionError(
            f"Unable to connect to MongoDB at {settings.MONGO_URI}. Start MongoDB locally and retry."
        ) from exc
    return client


def get_database() -> Database:
    return get_client()[settings.MONGO_DB_NAME]


def get_complaints_collection() -> Collection:
    return get_database()[settings.COMPLAINTS_COLLECTION]


def get_users_collection() -> Collection:
    return get_database()[settings.USERS_COLLECTION]


def ping_database() -> bool:
    try:
        get_client().admin.command("ping")
        return True
    except Exception:
        return False
