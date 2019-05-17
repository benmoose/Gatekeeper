from datetime import datetime, timedelta

import jwt
import pytest
import pytz

from common.time import to_timestamp
from db.user import get_or_create_user

from .jwt import generate_access_token_for_user, generate_refresh_token_for_user


@pytest.fixture
def current_time():
    return datetime(2020, 1, 1, tzinfo=pytz.UTC)


@pytest.fixture
def user():
    user, _ = get_or_create_user("+447000000000")
    return user


@pytest.mark.django_db
def test_generate_refresh_token_for_user(settings, rsa_keys, current_time, user):
    settings.AUTH_ACCESS_TOKEN_AUDIENCE = "audience-url"
    settings.AUTH_ACCESS_TOKEN_ISSUER = "gatekeeper-url"

    refresh_token, payload = generate_refresh_token_for_user(
        user, current_time, "token-id"
    )
    assert isinstance(refresh_token, str)
    assert isinstance(payload, dict)
    assert {"typ": "JWT", "alg": "RS256"} == jwt.get_unverified_header(refresh_token)
    assert {
        "sub": user.user_id,
        "iat": to_timestamp(current_time),
        "exp": to_timestamp(current_time + timedelta(days=365)),
        "typ": "refresh",
        "aud": "audience-url",
        "iss": "gatekeeper-url",
        "jti": "token-id",
    } == jwt.decode(
        refresh_token,
        rsa_keys.public_key,
        algorithms=["RS256"],
        audience="audience-url",
    )


@pytest.mark.django_db
def test_generate_access_token_from_refresh_token(
    settings, rsa_keys, current_time, user
):
    settings.AUTH_ACCESS_TOKEN_AUDIENCE = "audience-url"
    settings.AUTH_ACCESS_TOKEN_ISSUER = "gatekeeper-url"

    access_token, payload = generate_access_token_for_user(user, current_time)
    assert isinstance(access_token, str)
    assert isinstance(payload, dict)
    assert {
        "sub": user.user_id,
        "iat": to_timestamp(current_time),
        "exp": to_timestamp(current_time + timedelta(hours=1)),
        "typ": "access",
        "aud": "audience-url",
        "iss": "gatekeeper-url",
    } == jwt.decode(
        access_token, rsa_keys.public_key, algorithms=["RS256"], audience="audience-url"
    )
