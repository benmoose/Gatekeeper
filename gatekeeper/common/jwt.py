from datetime import datetime, timedelta
from typing import Optional, Tuple

import jwt
from django.conf import settings

from common.generate import generate_id
from common.time import to_timestamp
from db.models import User

REFRESH_TOKEN_EXPIRY_TIME_SECONDS = 365 * 24 * 60 * 60  # one year
ACCESS_TOKEN_EXPIRY_TIME_SECONDS = 60 * 60  # one hour

JWT_ALGORITHM = "RS256"
JWT_TYPE = "JWT"

ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"


def generate_refresh_token_for_user(
    user: User, current_time: datetime, token_id: str
) -> Tuple[str, dict]:
    expiry_time = current_time + timedelta(seconds=REFRESH_TOKEN_EXPIRY_TIME_SECONDS)
    payload = _get_refresh_jwt_payload(
        user_id=user.user_id,
        issuing_time=current_time,
        expiry_time=expiry_time,
        is_refresh_token=True,
        token_id=token_id,
    )
    return encode_token(payload), payload


def generate_access_token_for_user(
    user: User, current_time: datetime
) -> Tuple[str, dict]:
    expiry_time = current_time + timedelta(seconds=ACCESS_TOKEN_EXPIRY_TIME_SECONDS)
    payload = _get_access_token_jwt_payload(
        user_id=user.user_id,
        issuing_time=current_time,
        expiry_time=expiry_time,
        is_refresh_token=False,
    )
    return encode_token(payload), payload


def decode_token(token: str) -> Optional[dict]:
    try:
        with open(settings.AUTH_PUBLIC_KEY_PATH, "rb") as public_key:
            return jwt.decode(
                jwt=token,
                key=public_key.read(),
                algorithms=[JWT_ALGORITHM],
                audience=settings.AUTH_ACCESS_TOKEN_AUDIENCE,
            )
    except jwt.exceptions.InvalidTokenError:
        return None


def encode_token(payload: dict) -> str:
    with open(settings.AUTH_PRIVATE_KEY_PATH, "rb") as private_key:
        return jwt.encode(
            payload=payload,
            key=private_key.read(),
            algorithm=JWT_ALGORITHM,
            headers=_get_jwt_headers(),
        ).decode("UTF-8")


def generate_refresh_token_id() -> str:
    return generate_id("refreshtoken")


def _get_jwt_headers() -> dict:
    return {"alg": JWT_ALGORITHM, "typ": JWT_TYPE}


def _get_refresh_jwt_payload(
    user_id: str,
    issuing_time: datetime,
    expiry_time: datetime,
    is_refresh_token: bool,
    token_id: str,
):
    return _get_jwt_payload(
        user_id, issuing_time, expiry_time, is_refresh_token, jti=token_id
    )


def _get_access_token_jwt_payload(
    user_id: str, issuing_time: datetime, expiry_time: datetime, is_refresh_token: bool
):
    return _get_jwt_payload(user_id, issuing_time, expiry_time, is_refresh_token)


def _get_jwt_payload(
    user_id: str,
    issuing_time: datetime,
    expiry_time: datetime,
    is_refresh_token: bool,
    **extra
) -> dict:
    return {
        "sub": user_id,
        "iat": to_timestamp(issuing_time),
        "exp": to_timestamp(expiry_time),
        "aud": settings.AUTH_ACCESS_TOKEN_AUDIENCE,
        "iss": settings.AUTH_ACCESS_TOKEN_ISSUER,
        "typ": REFRESH_TOKEN_TYPE if is_refresh_token else ACCESS_TOKEN_TYPE,
        **extra,
    }
