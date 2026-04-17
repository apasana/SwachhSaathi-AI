from __future__ import annotations

import hashlib
import os

from fastapi import HTTPException

from database.mongo import MongoConnectionError, get_users_collection
from models.schemas import UserLogin, UserRegister
from utils.helpers import serialize_document


def _hash_password(password: str, salt: bytes) -> str:
    key = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 120000)
    return key.hex()


class AuthService:
    def register_user(self, payload: UserRegister) -> dict:
        try:
            users = get_users_collection()
        except MongoConnectionError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

        existing = users.find_one({"$or": [{"username": payload.username.lower()}, {"contact_number": payload.contact_number}]})
        if existing:
            raise HTTPException(status_code=409, detail="User already exists with this username or contact number")

        salt = os.urandom(16)
        password_hash = _hash_password(payload.password, salt)

        document = {
            "username": payload.username.lower(),
            "full_name": payload.full_name,
            "contact_number": payload.contact_number,
            "role": payload.role.value,
            "password_hash": password_hash,
            "password_salt": salt.hex(),
        }

        users.insert_one(document)
        public = {
            "username": document["username"],
            "full_name": document["full_name"],
            "contact_number": document["contact_number"],
            "role": document["role"],
        }
        return serialize_document(public)

    def login_user(self, payload: UserLogin) -> dict:
        try:
            users = get_users_collection()
        except MongoConnectionError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

        matched_users = list(users.find({"username": payload.username.lower()}))
        if not matched_users:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        valid_user = None
        for user in matched_users:
            salt_hex = user.get("password_salt", "")
            expected_hash = user.get("password_hash", "")
            if not salt_hex or not expected_hash:
                continue

            try:
                salt = bytes.fromhex(salt_hex)
            except ValueError:
                continue

            incoming_hash = _hash_password(payload.password, salt)
            if incoming_hash == expected_hash:
                valid_user = user
                break

        if valid_user is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        public = {
            "username": valid_user["username"],
            "full_name": valid_user["full_name"],
            "contact_number": valid_user["contact_number"],
            "role": valid_user["role"],
        }
        return serialize_document(public)


auth_service = AuthService()
