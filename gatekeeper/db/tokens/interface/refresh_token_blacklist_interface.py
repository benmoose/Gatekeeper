from datetime import datetime
from typing import Optional

from ...user.models import User
from ..models import RefreshTokenBlacklist


def blacklist_refresh_token(
    user: User, token_id: str, issued_at: datetime, expiry_time: datetime
) -> RefreshTokenBlacklist:
    blacklist_info, _ = RefreshTokenBlacklist.objects.get_or_create(
        user=user,
        token_id=token_id,
        token_issued_at=issued_at,
        token_expiry_time=expiry_time,
    )
    return blacklist_info


def get_refresh_token_blacklist_details(
    token_id: str
) -> Optional[RefreshTokenBlacklist]:
    try:
        return RefreshTokenBlacklist.objects.get(token_id=token_id)
    except RefreshTokenBlacklist.DoesNotExist:
        return None
