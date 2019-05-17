import logging
from typing import Optional, Tuple

from django.db import transaction

from ..models import User

logger = logging.getLogger(__name__)


def get_user_by_user_id(user_id: str) -> Optional[User]:
    try:
        return User.objects.get(user_id=user_id)
    except User.DoesNotExist:
        return None


def get_or_create_user(
    phone_number: str, full_name: str = "", short_name: str = "", picture: str = ""
) -> Tuple[User, bool]:
    return User.objects.get_or_create(
        phone_number=phone_number,
        defaults=dict(full_name=full_name, short_name=short_name, picture=picture),
    )


def set_user_as_inactive(user: User):
    with transaction.atomic():
        user = User.objects.select_for_update().get(pk=user.pk)
        if not user.is_active:
            return
        user.is_active = False
        user.save(update_fields=["is_active", "modified_on"])


def set_user_as_active(user: User):
    with transaction.atomic():
        user = User.objects.select_for_update().get(pk=user.pk)
        if user.is_active:
            return
        user.is_active = True
        user.save(update_fields=["is_active", "modified_on"])
