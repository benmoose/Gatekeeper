from datetime import datetime
from typing import Optional

from ...user.models import User
from ..models import RevokedRefreshToken


def create_revoked_refresh_token(
    user: User, token_id: str, issued_at: datetime, expiry_time: datetime
) -> RevokedRefreshToken:
    blacklist_info, _ = RevokedRefreshToken.objects.get_or_create(
        user=user,
        token_id=token_id,
        token_issued_at=issued_at,
        token_expires_at=expiry_time,
    )
    return blacklist_info


def is_refresh_token_revoked(token_id: str) -> bool:
    return RevokedRefreshToken.objects.filter(token_id=token_id).exists()


def get_revoked_refresh_token(token_id: str) -> Optional[RevokedRefreshToken]:
    try:
        return RevokedRefreshToken.objects.get(token_id=token_id)
    except RevokedRefreshToken.DoesNotExist:
        return None
