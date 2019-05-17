from datetime import timedelta

import pytest
from django.conf import settings
from django.db import IntegrityError

from db.user import get_or_create_user

from ..models.revoked_refresh_token import RevokedRefreshToken
from .revoked_refresh_token_interface import (
    create_revoked_refresh_token,
    get_revoked_refresh_token,
    is_refresh_token_revoked,
)


@pytest.fixture
def current_time():
    return settings.TEST_CURRENT_TIME


@pytest.fixture
def user():
    return get_or_create_user(phone_number="+447000000000")


@pytest.fixture
def refresh_token_blacklist(current_time, user):
    return RevokedRefreshToken(
        user=user,
        token_id="refresh:abc",
        token_issued_at=current_time,
        token_expires_at=current_time + timedelta(days=365),
    )


@pytest.mark.django_db
def test_create_revoked_refresh_token(current_time, user):
    assert 0 == len(RevokedRefreshToken.objects.all())
    revoked_refresh_token = create_revoked_refresh_token(
        user, "token-id", current_time, current_time + timedelta(days=365)
    )
    assert 1 == len(RevokedRefreshToken.objects.all())
    assert user == revoked_refresh_token.user
    assert "token-id" == revoked_refresh_token.token_id
    assert current_time == revoked_refresh_token.token_issued_at
    assert current_time + timedelta(days=365) == revoked_refresh_token.token_expires_at

    assert revoked_refresh_token == create_revoked_refresh_token(
        user, "token-id", current_time, current_time + timedelta(days=365)
    )
    assert 1 == len(RevokedRefreshToken.objects.all())


@pytest.mark.django_db
def test_get_refresh_token_blacklist_details(refresh_token_blacklist):
    refresh_token_blacklist.save()
    assert None is get_revoked_refresh_token(token_id="foo")
    assert refresh_token_blacklist == get_revoked_refresh_token(
        refresh_token_blacklist.token_id
    )


@pytest.mark.django_db
def test_get_refresh_token_blacklist_details(refresh_token_blacklist):
    refresh_token_blacklist.save()
    assert False is is_refresh_token_revoked(token_id="foo")
    assert True is is_refresh_token_revoked("refresh:abc")
