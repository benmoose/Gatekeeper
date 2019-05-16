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

from .jwt import generate_access_token_for_user


@pytest.fixture
def current_time():
    return datetime(2020, 1, 1, tzinfo=pytz.UTC)


@pytest.fixture
def user():
    return get_or_create_user("+447000000000")


@pytest.mark.django_db
def test_generate_access_token_for_user(settings, tmp_path, current_time, user):
    private_key_path = tmp_path / "private-key.pem"
    public_key, private_key = create_public_private_key_pair()

    settings.AUTH_PRIVATE_KEY_PATH = private_key_path
    settings.AUTH_ACCESS_TOKEN_AUDIENCE = "audience-url"
    settings.AUTH_ACCESS_TOKEN_ISSUER = "gatekeeper-url"

    with open(private_key_path, "wb") as f:
        f.write(private_key_to_bytes(private_key))

    token = generate_access_token_for_user(user, current_time)
    assert {"typ": "JWT", "alg": "RS256"} == jwt.get_unverified_header(token)
    assert {
        "sub": user.user_id,
        "exp": to_timestamp(current_time + timedelta(hours=2)),
        "aud": "audience-url",
        "iss": "gatekeeper-url",
    } == jwt.decode(token, public_key, algorithms=["RS256"], audience="audience-url")


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
