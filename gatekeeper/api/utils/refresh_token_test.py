from collections import namedtuple

import pytest
from django.conf import settings

from common.jwt import (
    generate_access_token_for_user,
    generate_refresh_token_for_user,
    generate_refresh_token_id,
)
from db.tokens import register_user_refresh_token
from db.user import get_or_create_user

from .refresh_token import get_refresh_token_payload_if_active

Token = namedtuple("Token", ("encoded", "payload"))


@pytest.fixture
def current_time():
    return settings.TEST_CURRENT_TIME


@pytest.fixture
def user():
    user, _ = get_or_create_user("+447000000000")
    return user


@pytest.fixture
def token_id():
    return generate_refresh_token_id()


@pytest.fixture
def refresh_token(current_time, token_id, user) -> Token:
    token, payload = generate_refresh_token_for_user(user, current_time, token_id)
    return Token(token, payload)


@pytest.mark.django_db
@pytest.mark.usefixtures("rsa_keys")
def test_get_refresh_token_payload_if_active(
    current_time, user, token_id, refresh_token
):
    access_token, _ = generate_access_token_for_user(user.user_id, current_time)
    assert None is get_refresh_token_payload_if_active(access_token)
    assert None is get_refresh_token_payload_if_active("")
    assert None is get_refresh_token_payload_if_active("foo")
    assert None is get_refresh_token_payload_if_active(refresh_token.encoded)

    register_user_refresh_token(user, token_id, refresh_token.payload)
    assert refresh_token.payload == get_refresh_token_payload_if_active(
        refresh_token.encoded
    )

    register_user_refresh_token(user, "newer-refresh-token", {})
    assert None is get_refresh_token_payload_if_active(refresh_token.encoded)
