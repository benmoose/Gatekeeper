from collections import namedtuple
from typing import Tuple

import pytest
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

RSAKeys = namedtuple("Keys", ("public_key", "private_key"))


@pytest.fixture
def rsa_keys(settings, tmp_path) -> RSAKeys:
    """
    Fixture for generating a public/private key pair and configuring Django to point to
    those keys so JWT cryptography works.
    """
    private_key_path = tmp_path / "private-key.pem"
    public_key_path = tmp_path / "public-key.pem"

    settings.AUTH_PUBLIC_KEY_PATH = public_key_path
    settings.AUTH_PRIVATE_KEY_PATH = private_key_path

    public_key, private_key = _create_public_private_key_pair()
    with open(public_key_path, "wb") as f:
        f.write(_public_key_to_bytes(public_key))
    with open(private_key_path, "wb") as f:
        f.write(_private_key_to_bytes(private_key))

    return RSAKeys(public_key=public_key, private_key=private_key)


def _create_public_private_key_pair() -> Tuple[rsa.RSAPublicKey, rsa.RSAPrivateKey]:
    private_key = rsa.generate_private_key(
        public_exponent=65537, key_size=2048, backend=default_backend()
    )
    return private_key.public_key(), private_key


def _private_key_to_bytes(private_key: rsa.RSAPrivateKey) -> bytes:
    return private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )


def _public_key_to_bytes(public_key: rsa.RSAPublicKey) -> bytes:
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
