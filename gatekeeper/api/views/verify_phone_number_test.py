import json
from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.test import Client
from django.urls import reverse

from common.test_utils import (
    create_public_private_key_pair,
    private_key_to_bytes,
    public_key_to_bytes,
)
from db.models import RefreshToken, User, VerificationCode

from .verify_phone_number import verify_phone_number


@pytest.fixture
def test_time() -> datetime:
    return settings.TEST_CURRENT_TIME


@pytest.fixture
def verification_code(test_time) -> VerificationCode:
    expiry_time = test_time + timedelta(minutes=5)
    return VerificationCode(
        phone_number="+447000000000", code="abcd", expires_at=expiry_time
    )


@pytest.fixture
def verification_code_expired(test_time) -> VerificationCode:
    expiry_time = test_time - timedelta(minutes=5)
    return VerificationCode(
        phone_number="+447000000000", code="abcd", expires_at=expiry_time
    )


@pytest.mark.parametrize(
    "request_data,expected_message",
    [
        ({}, "missing or invalid data"),
        ({"phone_number": "+447000000000"}, "missing or invalid data"),
        (
            {"phone_number": "+447000000000", "verification_code": "abc"},
            "invalid verification code",
        ),
    ],
)
@pytest.mark.django_db
def test_verify_phone_number_bad_request(request_data, expected_message):
    response = make_request(request_data)
    assert expected_message in response.content.decode("UTF-8")


@pytest.mark.django_db
def test_verify_phone_number(settings, tmp_path, verification_code):
    verification_code.save()

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

    assert 0 == len(User.objects.all())
    assert 0 == len(RefreshToken.objects.all())
    response = make_request(
        {"phone_number": "+447000000000", "verification_code": "abcd"}
    )
    assert 200 == response.status_code
    assert 1 == len(User.objects.all())
    assert 1 == len(RefreshToken.objects.all())
    assert "+447000000000" == User.objects.first().phone_number
    response_data = json.loads(response.content)
    assert {"refresh_token", "access_token", "expiry_time"} == response_data.keys()


@pytest.mark.django_db
def test_verify_phone_number_multiple_attempts(settings, tmp_path, verification_code):
    verification_code.save()

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

    assert 0 == len(User.objects.all())
    assert 0 == len(RefreshToken.objects.all())
    first_response = make_request(
        {"phone_number": "+447000000000", "verification_code": "abcd"}
    )
    assert 200 == first_response.status_code
    assert 1 == len(User.objects.all())
    assert 1 == len(RefreshToken.objects.all())
    second_response = make_request(
        {"phone_number": "+447000000000", "verification_code": "abcd"}
    )
    assert 400 == second_response.status_code
    assert b"phone number has already been verified" in second_response.content
    assert 1 == len(User.objects.all())
    assert 1 == len(RefreshToken.objects.all())


def make_request(data):
    client = Client()
    url = reverse(verify_phone_number)
    return client.post(url, data, content_type="application/json")
