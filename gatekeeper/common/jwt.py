from datetime import datetime, timedelta

import jwt
from django.conf import settings

from common.time import to_timestamp
from db.models import User

ACCESS_TOKEN_EXPIRY_TIME_SECONDS = 2 * 60 * 60  # two hours

JWT_ALGORITHM = "RS256"
JWT_TYPE = "JWT"


def generate_access_token_for_user(user: User, current_time: datetime) -> str:
    expiry_time = current_time + timedelta(seconds=ACCESS_TOKEN_EXPIRY_TIME_SECONDS)
    payload = get_jwt_payload_for_user(user, expiry_time)
    with open(settings.AUTH_PRIVATE_KEY_PATH, "rb") as private_key:
        return jwt.encode(
            payload=payload,
            key=private_key.read(),
            algorithm=JWT_ALGORITHM,
            headers=get_jwt_header(),
        ).decode("UTF-8")


def get_jwt_header() -> dict:
    return {"alg": JWT_ALGORITHM, "typ": JWT_TYPE}


def get_jwt_payload_for_user(user: User, expiry_time: datetime) -> dict:
    return {
        "sub": user.user_id,
        "exp": to_timestamp(expiry_time),
        "aud": settings.AUTH_ACCESS_TOKEN_AUDIENCE,
        "iss": settings.AUTH_ACCESS_TOKEN_ISSUER,
    }
