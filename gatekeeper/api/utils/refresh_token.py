from typing import Optional

from common.jwt import REFRESH_TOKEN_TYPE, decode_token
from db.tokens import get_latest_refresh_token_for_user


def get_refresh_token_payload_if_active(refresh_token: str) -> Optional[dict]:
    """
    Return refresh token payload if it's valid and the user's most recently issued
    refresh token, else returns None.
    """
    payload = decode_token(refresh_token)
    if payload is None:
        return None
    if not is_refresh_token_active(payload):
        return None
    return payload


def is_refresh_token_active(refresh_token_payload: dict) -> bool:
    """
    Return True if the refresh token's payload is well formed and has not been revoked.
    """
    if refresh_token_payload["typ"] != REFRESH_TOKEN_TYPE:
        return False
    expected_refresh_token = get_latest_refresh_token_for_user(
        user_id=refresh_token_payload["sub"]
    )
    if expected_refresh_token is None:
        return False
    if refresh_token_payload["jti"] != expected_refresh_token.token_id:
        return False
    return True
