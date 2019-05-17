from datetime import datetime, timedelta
from typing import Optional, Tuple

import jwt
from django.conf import settings

from common.generate import generate_id
from common.time import to_timestamp
from db.models import User
from db.tokens import is_refresh_token_revoked

REFRESH_TOKEN_EXPIRY_TIME_SECONDS = 365 * 24 * 60 * 60  # one year
ACCESS_TOKEN_EXPIRY_TIME_SECONDS = 60 * 60  # one hour

JWT_ALGORITHM = "RS256"
JWT_TYPE = "JWT"

ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"


def generate_refresh_token_for_user(
    user: User, current_time: datetime, token_id: str
) -> str:
    expiry_time = current_time + timedelta(seconds=REFRESH_TOKEN_EXPIRY_TIME_SECONDS)
    payload = get_refresh_jwt_payload(
        user_id=user.user_id,
        issuing_time=current_time,
        expiry_time=expiry_time,
        is_refresh_token=True,
        token_id=token_id,
    )
    with open(settings.AUTH_PRIVATE_KEY_PATH, "rb") as private_key:
        return jwt.encode(
            payload=payload,
            key=private_key.read(),
            algorithm=JWT_ALGORITHM,
            headers=get_jwt_headers(),
        ).decode("UTF-8")


def generate_access_token_from_refresh_token(
    refresh_token: str, current_time: datetime
) -> Optional[Tuple[str, datetime]]:
    refresh_token_payload = get_refresh_token_payload_if_valid(refresh_token)
    if refresh_token_payload is None:
        return None

    expiry_time = current_time + timedelta(seconds=ACCESS_TOKEN_EXPIRY_TIME_SECONDS)
    refresh_token_id = refresh_token_payload["jti"]
    payload = get_access_token_jwt_payload(
        user_id=refresh_token_payload["sub"],
        issuing_time=current_time,
        expiry_time=expiry_time,
        is_refresh_token=False,
        refresh_token_id=refresh_token_id,
    )
    with open(settings.AUTH_PRIVATE_KEY_PATH, "rb") as private_key:
        access_token = jwt.encode(
            payload=payload,
            key=private_key.read(),
            algorithm=JWT_ALGORITHM,
            headers=get_jwt_headers(),
        ).decode("UTF-8")
    return access_token, expiry_time


def get_refresh_token_payload_if_valid(refresh_token: str) -> Optional[dict]:
    with open(settings.AUTH_PUBLIC_KEY_PATH, "rb") as public_key:
        payload = jwt.decode(
            jwt=refresh_token,
            key=public_key.read(),
            algorithms=[JWT_ALGORITHM],
            audience=settings.AUTH_ACCESS_TOKEN_AUDIENCE,
        )
    if payload["typ"] != REFRESH_TOKEN_TYPE:
        return None
    if is_refresh_token_revoked(token_id=payload["jti"]):
        return None
    return payload


def get_jwt_headers() -> dict:
    return {"alg": JWT_ALGORITHM, "typ": JWT_TYPE}


def get_refresh_jwt_payload(
    user_id: str,
    issuing_time: datetime,
    expiry_time: datetime,
    is_refresh_token: bool,
    token_id: str,
):
    return get_jwt_payload(
        user_id, issuing_time, expiry_time, is_refresh_token, jti=token_id
    )


def get_access_token_jwt_payload(
    user_id: str,
    issuing_time: datetime,
    expiry_time: datetime,
    is_refresh_token: bool,
    refresh_token_id: str,
):
    return get_jwt_payload(
        user_id, issuing_time, expiry_time, is_refresh_token, src=refresh_token_id
    )


def get_jwt_payload(
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


def generate_refresh_token_id() -> str:
    return generate_id("refreshtoken")
