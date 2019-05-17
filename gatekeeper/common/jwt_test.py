from datetime import datetime, timedelta

import jwt
import pytest
import pytz

from common.test_utils import (
    create_public_private_key_pair,
    private_key_to_bytes,
    public_key_to_bytes,
)
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
def test_generate_refresh_token_for_user(settings, tmp_path, current_time, user):
    private_key_path = tmp_path / "private-key.pem"

    settings.AUTH_PRIVATE_KEY_PATH = private_key_path
    settings.AUTH_ACCESS_TOKEN_AUDIENCE = "audience-url"
    settings.AUTH_ACCESS_TOKEN_ISSUER = "gatekeeper-url"

    public_key, private_key = create_public_private_key_pair()
    with open(private_key_path, "wb") as f:
        f.write(private_key_to_bytes(private_key))

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
        refresh_token, public_key, algorithms=["RS256"], audience="audience-url"
    )


@pytest.mark.django_db
def test_generate_access_token_from_refresh_token(
    settings, tmp_path, current_time, user
):
    private_key_path = tmp_path / "private-key.pem"
    public_key_path = tmp_path / "public-key.pem"

    settings.AUTH_PUBLIC_KEY_PATH = public_key_path
    settings.AUTH_PRIVATE_KEY_PATH = private_key_path
    settings.AUTH_ACCESS_TOKEN_AUDIENCE = "audience-url"
    settings.AUTH_ACCESS_TOKEN_ISSUER = "gatekeeper-url"

    public_key, private_key = create_public_private_key_pair()
    with open(public_key_path, "wb") as f:
        f.write(public_key_to_bytes(public_key))
    with open(private_key_path, "wb") as f:
        f.write(private_key_to_bytes(private_key))

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
        access_token, public_key, algorithms=["RS256"], audience="audience-url"
    )
