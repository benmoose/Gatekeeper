from typing import Optional

from db.tokens import get_latest_refresh_token_for_user
from common.jwt import decode_token, REFRESH_TOKEN_TYPE


def get_refresh_token_payload_if_valid(refresh_token: str) -> Optional[dict]:
    """
    Return token payload if it's valid and the user's most recently issued refresh
    token.
    """
    payload = decode_token(refresh_token)
    if payload["typ"] != REFRESH_TOKEN_TYPE:
        return None
    expected_refresh_token = get_latest_refresh_token_for_user(user_id=payload["sub"])
    if expected_refresh_token is None:
        return None
    if payload["jti"] != expected_refresh_token.token_id:
        return None
    return payload
