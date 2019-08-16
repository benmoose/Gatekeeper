from datetime import datetime
from string import ascii_letters

import pytest
import pytz
from django.test import Client
from django.urls import reverse

from coms.providers.mock_provider import MockProvider
from db.models import VerificationCode
from db.verification import create_verification_code

from .send_verification_code import (
    create_verification_code_with_retries,
    send_verification_code,
    send_verification_code_sms,
)


@pytest.fixture
def mock_provider() -> MockProvider:
    mock_provider = MockProvider.get_provider()
    yield mock_provider
    mock_provider.reset()


@pytest.mark.parametrize(
    "request_data",
    [
        {},
        {"foo": "bar"},
        {"phone_number": "+447000000000"},
        {"region": "GB"},
        {"phone_number": "foo", "region": "GB"},
        {"phone_number": "07000000000", "region": "FOO"},
    ],
)
def test_send_verification_code_bad_request(request_data):
    response = make_request(data=request_data)
    assert 400 == response.status_code


@pytest.mark.django_db
def test_send_verification_code_makes_request(settings, mock_provider):
    settings.TWILIO_MESSAGE_STATUS_CALLBACK = "/callback/"

    response = make_request({"phone_number": "07000000000", "region": "gb"})

    assert 200 == response.status_code
    assert b'{"phone_number": "+447000000000"}' == response.content

    sent_sms_messages = mock_provider.send_sms_attempts
    assert 1 == len(sent_sms_messages)
    phone_number, message, callback = sent_sms_messages[0]
    assert "+447000000000" == phone_number
    assert "Your verification code is " in message
    assert "/callback/" == callback

    assert 1 == len(VerificationCode.objects.all())
    verification_code = VerificationCode.objects.first()
    assert "+447000000000" == verification_code.phone_number
    assert verification_code.is_active


@pytest.mark.django_db
def test_send_verification_code_sms_returns_verification_code(mock_provider):
    success, verification_code = send_verification_code_sms(
        provider=mock_provider,
        phone_number="+447000000000",
        callback="/callback/",
        verification_code_population=ascii_letters,
        verification_code_length=4,
        verification_code_expiry_time=datetime(2020, 1, 1, tzinfo=pytz.utc),
    )
    assert True is success
    assert isinstance(verification_code, VerificationCode)


@pytest.mark.django_db
def test_send_verification_code_sms_makes_sms_provider_request(mock_provider):
    success, verification_code = send_verification_code_sms(
        provider=mock_provider,
        phone_number="+447000000000",
        callback="/callback/",
        verification_code_population=ascii_letters,
        verification_code_length=4,
        verification_code_expiry_time=datetime(2020, 1, 1, tzinfo=pytz.utc),
    )
    assert True is success
    assert 1 == len(mock_provider.send_sms_attempts)
    to_number, message, status_callback = mock_provider.send_sms_attempts[0]
    assert "+447000000000" == to_number
    assert "Your verification code is " in message
    assert "/callback/" == status_callback


@pytest.mark.django_db
def test_create_verification_code_with_retries_returns_verification_code():
    code = create_verification_code_with_retries(
        phone_number="+447000000000",
        verification_code_population="abc",
        verification_code_length=2,
        verification_code_expiry_time=datetime(2020, 1, 1, tzinfo=pytz.UTC),
        max_retries=1,
    )
    assert isinstance(code, VerificationCode)


@pytest.mark.django_db(transaction=True)
def test_create_verification_code_with_retries_raises_if_max_retries_reached():
    expiry_time = datetime(2020, 1, 1, tzinfo=pytz.UTC)

    # create pre-existing expiry code
    create_verification_code("+447000111222", "a", expiry_time)

    # attempt to create different expiry code (impossible)
    with pytest.raises(RuntimeError):
        create_verification_code_with_retries(
            phone_number="+447000000000",
            verification_code_population=["a"],
            verification_code_length=1,
            verification_code_expiry_time=expiry_time,
            max_retries=1,
        )

    assert 1 == len(VerificationCode.objects.all())


def make_request(data):
    client = Client()
    url = reverse(send_verification_code)
    return client.post(url, data, content_type="application/json")
