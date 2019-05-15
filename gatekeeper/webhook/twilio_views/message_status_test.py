import json
from pathlib import Path

import pytest
from django.test import Client
from django.urls import reverse

from .message_status import message_status_webhook

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture(scope="module")
def api_client():
    return Client()


@pytest.fixture
def url():
    return reverse(message_status_webhook)


@pytest.fixture
def request_data():
    return json.loads(read_fixture("sms-webhook-request.json"))


@pytest.mark.parametrize(
    "request_data", [{}, {"message_sid": "msg-sid-xxx", "sms_sid": "sms-sid-xxx"}]
)
def test_message_status_bad_request(api_client, url, request_data):
    response = api_client.post(url, request_data)
    assert 400 == response.status_code


def test_message_status(api_client, url, request_data):
    response = api_client.post(url, request_data)
    assert 200 == response.status_code


def read_fixture(fixture_name):
    fixture_path = FIXTURES_DIR / fixture_name
    with open(fixture_path) as f:
        return f.read()
