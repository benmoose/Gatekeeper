import json
from datetime import datetime, timedelta

import pytest
from django.conf import settings
from django.test import Client
from django.urls import reverse

from db.models import User, VerificationCode

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
def test_verify_phone_number(verification_code):
    verification_code.save()

    assert 0 == len(User.objects.all())
    response = make_request(
        {"phone_number": "+447000000000", "verification_code": "abcd"}
    )
    assert 200 == response.status_code
    assert 1 == len(User.objects.all())
    assert "+447000000000" == User.objects.first().phone_number
    response_data = json.loads(response.content)
    assert {
        "user_id",
        "phone_number",
        "created_on",
        "modified_on",
    } == response_data.keys()
    assert "+447000000000" == response_data["phone_number"]
    user = User.objects.all()[0]
    assert user.user_id == response_data["user_id"]


@pytest.mark.django_db
def test_verify_phone_number_idempotent(verification_code):
    verification_code.save()

    assert 0 == len(User.objects.all())
    make_request({"phone_number": "+447000000000", "verification_code": "abcd"})
    assert 1 == len(User.objects.all())
    make_request({"phone_number": "+447000000000", "verification_code": "abcd"})
    assert 1 == len(User.objects.all())


def make_request(data):
    client = Client()
    url = reverse(verify_phone_number)
    return client.post(url, data, content_type="application/json")
