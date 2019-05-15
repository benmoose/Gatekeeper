from datetime import datetime, timedelta

import pytest
import pytz
from django.test import Client
from django.urls import reverse

import api
from common.test import mock_current_time
from db_layer.models import User, VerificationCode
from db_layer.verification import create_verification_code

from .verify_phone_number import verify_phone_number


@pytest.fixture
def expiry_time() -> datetime:
    return datetime(2019, 1, 1, tzinfo=pytz.UTC)


@pytest.fixture
def verification_code(expiry_time) -> VerificationCode:
    return create_verification_code("+447000000000", "abcd", expiry_time)


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
def test_verify_phone_number(expiry_time, verification_code):
    assert 0 == len(User.objects.all())

    mock_time = expiry_time - timedelta(minutes=5)
    with mock_current_time(api.views.verify_phone_number, mock_time):
        response = make_request(
            {"phone_number": "+447000000000", "verification_code": "abcd"}
        )

    assert 200 == response.status_code
    assert 1 == len(User.objects.all())
    assert "+447000000000" == User.objects.first().phone_number


def make_request(data):
    client = Client()
    url = reverse(verify_phone_number)
    return client.post(url, data)
