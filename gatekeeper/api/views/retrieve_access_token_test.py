from collections import namedtuple

import pytest
from django.conf import settings
from django.test import Client
from django.urls import reverse

from common.jwt import (
    decode_token,
    generate_access_token_for_user,
    generate_refresh_token_for_user,
    generate_refresh_token_id,
    get_access_token_expiry_time,
)
from common.response import HTTP_400_BAD_REQUEST
from common.time import to_timestamp
from db.tokens import register_user_refresh_token
from db.user import get_or_create_user

from .retrieve_access_token import retrieve_access_token

Token = namedtuple("Token", ("encoded", "payload"))


@pytest.fixture
def current_time():
    return settings.TEST_CURRENT_TIME


@pytest.fixture
def user():
    user, _ = get_or_create_user("+447000000000")
    return user


@pytest.fixture
def token_id():
    return generate_refresh_token_id()


@pytest.fixture
def refresh_token(current_time, token_id, user) -> Token:
    token, payload = generate_refresh_token_for_user(user, current_time, token_id)
    return Token(token, payload)


@pytest.mark.django_db
@pytest.mark.usefixtures("rsa_keys")
@pytest.mark.parametrize(
    "status_code,request_data",
    [
        (HTTP_400_BAD_REQUEST, {}),
        (HTTP_400_BAD_REQUEST, {"refresh_token": 123}),
        (HTTP_400_BAD_REQUEST, {"refresh_token": ""}),
    ],
)
def test_retrieve_access_token_bad_request(status_code, request_data):
    response = make_request(request_data)
    assert status_code == response.status_code


@pytest.mark.django_db
@pytest.mark.usefixtures("rsa_keys")
def test_retrieve_access_token_invalid_refresh_token(refresh_token):
    response = make_request({"refresh_token": refresh_token.encoded})
    assert 400 == response.status_code
    assert b"token is invalid" in response.content


@pytest.mark.django_db
@pytest.mark.usefixtures("rsa_keys")
def test_retrieve_access_token_with_access_token(current_time, user):
    access_token, _ = generate_access_token_for_user(user.user_id, current_time)
    response = make_request({"refresh_token": access_token})
    assert 400 == response.status_code
    assert b"token is invalid" in response.content


@pytest.mark.django_db
@pytest.mark.usefixtures("rsa_keys")
def test_retrieve_access_token(current_time, user, token_id, refresh_token):
    register_user_refresh_token(user, token_id, refresh_token.payload)
    response = make_request({"refresh_token": refresh_token.encoded})
    assert 200 == response.status_code

    response_data = response.json()
    assert {"access_token", "expiry_time"} == response_data.keys()

    payload = decode_token(response_data["access_token"])
    expiry_time = get_access_token_expiry_time(current_time)
    assert isinstance(payload, dict)
    assert user.user_id == payload["sub"]
    assert to_timestamp(expiry_time) == payload["exp"]
    assert expiry_time.isoformat() == response_data["expiry_time"]


def make_request(data):
    client = Client()
    url = reverse(retrieve_access_token)
    return client.post(url, data, content_type="application/json")
