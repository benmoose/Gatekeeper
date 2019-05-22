import json
from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.test import Client
from django.urls import reverse

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
        ({}, "Missing or invalid data"),
        ({"phone_number": "+447000000000"}, "Missing or invalid data"),
        (
            {"phone_number": "+447000000000", "verification_code": "abc"},
            "Invalid verification code",
        ),
    ],
)
@pytest.mark.django_db
def test_verify_phone_number_bad_request(request_data, expected_message):
    response = make_request(request_data)
    assert expected_message in response.content.decode("UTF-8")


@pytest.mark.django_db
@pytest.mark.usefixtures("rsa_keys")
def test_verify_phone_number(settings, verification_code):
    verification_code.save()

    settings.AUTH_ACCESS_TOKEN_AUDIENCE = "audience-url"
    settings.AUTH_ACCESS_TOKEN_ISSUER = "gatekeeper-url"

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
@pytest.mark.usefixtures("rsa_keys")
def test_verify_phone_number_multiple_attempts(settings, verification_code):
    verification_code.save()

    settings.AUTH_ACCESS_TOKEN_AUDIENCE = "audience-url"
    settings.AUTH_ACCESS_TOKEN_ISSUER = "gatekeeper-url"

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
    assert b"Invalid verification code" in second_response.content
    assert 1 == len(User.objects.all())
    assert 1 == len(RefreshToken.objects.all())


def make_request(data):
    client = Client()
    url = reverse(verify_phone_number)
    return client.post(url, data, content_type="application/json")
