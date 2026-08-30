import os
import secrets
from datetime import datetime, timedelta, timezone
from functools import lru_cache

import jwt

from logassistant.core import BussinessException

ALGORITHM = "HS256"


@lru_cache
def _get_jwt_secret_key() -> str:
    return os.environ["JWT_SECRET_KEY"]


@lru_cache
def _get_internal_secret_key() -> str:
    return os.environ["INTERNAL_CLIENT_SECRET"]


class AuthService:
    @staticmethod
    def authenticate_client(client_secret: str) -> str:
        if not secrets.compare_digest(client_secret, _get_internal_secret_key()):
            raise BussinessException("INVALID")

        payload = {
            "iss": "logassistant-backend",
            "sub": "logassistant-frontend",
            "scope": "trusted_client",
            "exp": datetime.now(timezone.utc) + timedelta(minutes=30),
        }

        return jwt.encode(payload, _get_jwt_secret_key(), algorithm=ALGORITHM)

    @staticmethod
    def verify_machine_token(token: str) -> dict:
        try:
            payload = jwt.decode(token, _get_jwt_secret_key(), algorithms=[ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            raise BussinessException("EXPIRED")
        except jwt.InvalidTokenError:
            raise BussinessException("INVALID")
