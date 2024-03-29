import pytest
from django.conf import settings

from common.jwt import (
    generate_access_token_for_user,
    generate_refresh_token_for_user,
    generate_refresh_token_id,
)
from db.tokens import register_user_refresh_token
from db.user import get_or_create_user

from .refresh_token import get_refresh_token_payload_if_active, is_refresh_token_active


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


@pytest.mark.django_db
@pytest.mark.usefixtures("rsa_keys")
def test_get_refresh_token_payload_if_active(current_time, user, token_id):
    refresh_token, refresh_token_payload = generate_refresh_token_for_user(
        user, current_time, token_id
    )

    access_token, _ = generate_access_token_for_user(user.user_id, current_time)
    assert None is get_refresh_token_payload_if_active(access_token)
    assert None is get_refresh_token_payload_if_active("")
    assert None is get_refresh_token_payload_if_active("foo")
    assert None is get_refresh_token_payload_if_active(refresh_token)

    register_user_refresh_token(user, token_id, refresh_token_payload)
    assert refresh_token_payload == get_refresh_token_payload_if_active(refresh_token)

    register_user_refresh_token(user, "newer-refresh-token", {"jti": "foo"})
    assert refresh_token_payload == get_refresh_token_payload_if_active(refresh_token)


@pytest.mark.django_db
@pytest.mark.usefixtures("rsa_keys")
def test_is_refresh_token_active_supports_multiple_active_refresh_tokens(
    current_time, user
):
    _, refresh_token_1_payload = generate_refresh_token_for_user(
        user, current_time, "token-1"
    )
    _, refresh_token_2_payload = generate_refresh_token_for_user(
        user, current_time, "token-2"
    )
    register_user_refresh_token(user, "token-1", refresh_token_1_payload)
    register_user_refresh_token(user, "token-2", refresh_token_2_payload)

    assert True is is_refresh_token_active(refresh_token_1_payload)
    assert True is is_refresh_token_active(refresh_token_2_payload)
