from datetime import datetime, timedelta
from typing import Tuple

import jwt
import pytest
import pytz
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from common.time import to_timestamp
from db.user import get_or_create_user

from .jwt import (
    generate_access_token_from_refresh_token,
    generate_refresh_token_for_user,
)


@pytest.fixture
def current_time():
    return datetime(2020, 1, 1, tzinfo=pytz.UTC)


@pytest.fixture
def user():
    return get_or_create_user("+447000000000")


@pytest.mark.django_db
def test_generate_refresh_token_for_user(settings, tmp_path, current_time, user):
    private_key_path = tmp_path / "private-key.pem"

    settings.AUTH_PRIVATE_KEY_PATH = private_key_path
    settings.AUTH_ACCESS_TOKEN_AUDIENCE = "audience-url"
    settings.AUTH_ACCESS_TOKEN_ISSUER = "gatekeeper-url"

    public_key, private_key = create_public_private_key_pair()
    with open(private_key_path, "wb") as f:
        f.write(private_key_to_bytes(private_key))

    refresh_token = generate_refresh_token_for_user(user, current_time)
    assert isinstance(refresh_token, str)
    assert {"typ": "JWT", "alg": "RS256"} == jwt.get_unverified_header(refresh_token)
    assert {
        "sub": user.user_id,
        "iat": to_timestamp(current_time),
        "exp": to_timestamp(current_time + timedelta(days=365)),
        "typ": "refresh",
        "aud": "audience-url",
        "iss": "gatekeeper-url",
    } == jwt.decode(
        refresh_token, public_key, algorithms=["RS256"], audience="audience-url"
    )


@pytest.mark.django_db
def test_generate_access_token_from_refresh_token(
    settings, tmp_path, current_time, user
):
    private_key_path = tmp_path / "private-key.pem"
    public_key_path = tmp_path / "public-key.pem"

    settings.AUTH_PRIVATE_KEY_PATH = private_key_path
    settings.AUTH_PUBLIC_KEY_PATH = public_key_path
    settings.AUTH_ACCESS_TOKEN_AUDIENCE = "audience-url"
    settings.AUTH_ACCESS_TOKEN_ISSUER = "gatekeeper-url"

    public_key, private_key = create_public_private_key_pair()
    with open(private_key_path, "wb") as f:
        f.write(private_key_to_bytes(private_key))
    with open(public_key_path, "wb") as f:
        f.write(public_key_to_bytes(public_key))

    refresh_token = generate_refresh_token_for_user(user, current_time)
    access_token = generate_access_token_from_refresh_token(refresh_token, current_time)
    assert isinstance(access_token, str)


def create_public_private_key_pair() -> Tuple[rsa.RSAPublicKey, rsa.RSAPrivateKey]:
    private_key = rsa.generate_private_key(
        public_exponent=65537, key_size=2048, backend=default_backend()
    )
    return private_key.public_key(), private_key


def private_key_to_bytes(private_key: rsa.RSAPrivateKey) -> bytes:
    return private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )


def public_key_to_bytes(public_key: rsa.RSAPublicKey) -> bytes:
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
