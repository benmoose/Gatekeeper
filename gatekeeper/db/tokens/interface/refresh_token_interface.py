from typing import Optional
from ...user.models import User
from ..models import RefreshToken


def record_user_refresh_token(user: User, token_id: str, token_payload: dict) -> RefreshToken:
    return RefreshToken.objects.create(
        user=user,
        token_id=token_id,
        token_payload=token_payload,
    )


def get_latest_refresh_token_for_user(user_id: str) -> Optional[RefreshToken]:
    tokens = RefreshToken.objects.filter(user_id=user_id).order_by("-token_payload__iat")
    if len(tokens) == 0:
        return None
    return tokens[0]
