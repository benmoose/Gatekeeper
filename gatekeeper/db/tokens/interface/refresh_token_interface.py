from typing import List

from ...user.models import User
from ..models import RefreshToken


def register_user_refresh_token(
    user: User, token_id: str, payload: dict
) -> RefreshToken:
    return RefreshToken.objects.create(
        user=user, token_id=token_id, token_payload=payload
    )


def get_active_refresh_tokens_for_user(user_id: str) -> List[RefreshToken]:
    return list(
        RefreshToken.objects.filter(user_id=user_id).order_by("-token_payload__iat")
    )


def delete_refresh_token(token_id: str) -> bool:
    del_count, _ = RefreshToken.objects.filter(token_id=token_id).delete()
    return del_count > 0
