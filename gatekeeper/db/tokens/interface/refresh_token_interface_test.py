from datetime import timedelta

import pytest
from django.conf import settings

from common.time import to_timestamp
from db.user import get_or_create_user

from ..models import RefreshToken
from .refresh_token_interface import (
    delete_refresh_token,
    get_latest_refresh_token_for_user,
)


@pytest.fixture
def current_time():
    return settings.TEST_CURRENT_TIME


@pytest.fixture
def user():
    user, _ = get_or_create_user("+447000000000")
    return user


@pytest.mark.django_db
def test_get_latest_refresh_token_for_user(current_time, user):
    assert None is get_latest_refresh_token_for_user(user)

    refresh_token_1 = RefreshToken.objects.create(
        user=user,
        token_id="t1",
        token_payload={
            "sub": user.user_id,
            "iat": to_timestamp(current_time),
            "jti": "t1",
        },
    )
    assert refresh_token_1 == get_latest_refresh_token_for_user(user.user_id)

    refresh_token_2 = RefreshToken.objects.create(
        user=user,
        token_id="t2",
        token_payload={
            "sub": user.user_id,
            "iat": to_timestamp(current_time + timedelta(days=42)),
            "jti": "t2",
        },
    )
    assert refresh_token_2 == get_latest_refresh_token_for_user(user.user_id)


@pytest.mark.django_db
def test_delete_refresh_token(current_time, user):
    refresh_token = RefreshToken.objects.create(
        user=user,
        token_id="t1",
        token_payload={
            "sub": user.user_id,
            "iat": to_timestamp(current_time),
            "jti": "t1",
        },
    )
    assert 1 == len(RefreshToken.objects.all())
    success = delete_refresh_token(token_id=refresh_token.token_id)
    assert True is success
    assert 0 == len(RefreshToken.objects.all())

    success = delete_refresh_token(token_id=refresh_token.token_id)
    assert False is success
