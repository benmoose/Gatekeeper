from datetime import datetime

import pytest
import pytz
from django.test import Client
from django.urls import reverse

from coms.providers import get_communication_provider
from coms.providers.mock_provider import MockProvider
from db.models import VerificationCode
from db.verification import create_verification_code

from .send_verification_code import send_verification_code, send_verification_code_sms


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
def test_send_verification_code(settings):
    settings.TWILIO_MESSAGE_STATUS_CALLBACK = "/callback/"

    response = make_request({"phone_number": "07000000000", "region": "gb"})

    assert 200 == response.status_code
    assert b'{"phone_number": "+447000000000"}' == response.content

    provider = MockProvider.get_provider()
    sent_sms_messages = provider.send_sms_attempts
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
def test_send_verification_code_sms_max_retries_reached():
    expiry_time = datetime(2019, 1, 1, tzinfo=pytz.UTC)
    create_verification_code("+447000111222", "a", expiry_time)

    success, verification_code = send_verification_code_sms(
        provider=get_communication_provider(),
        phone_number="+447000000000",
        callback="/callback",
        verification_code_population=["a"],
        verification_code_length=1,
        verification_code_expiry_time=expiry_time,
        max_retries=3,
    )

    assert False is success
    assert None is verification_code
    assert 1 == len(VerificationCode.objects.all())


def make_request(data):
    client = Client()
    url = reverse(send_verification_code)
    return client.post(url, data, content_type="application/json")
