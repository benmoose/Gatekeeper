from collections import namedtuple

import pytest
from django.conf import settings
from django.test import Client
from django.urls import reverse

from common.jwt import (
    generate_access_token_for_user,
    generate_refresh_token_for_user,
    generate_refresh_token_id,
)
from db.models import RefreshToken
from db.tokens import register_user_refresh_token
from db.user import get_or_create_user

from .revoke_refresh_token import revoke_refresh_token

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
def test_revoke_refresh_token_invalid_tokens(current_time, user):
    response = make_request({"refresh_token": "this is not a valid token"})
    assert 400 == response.status_code

    access_token, _ = generate_access_token_for_user(user.user_id, current_time)
    response = make_request({"refresh_token": access_token})
    assert 400 == response.status_code


@pytest.mark.django_db
@pytest.mark.usefixtures("rsa_keys")
def test_revoke_refresh_token(user, token_id, refresh_token):
    register_user_refresh_token(user, token_id, refresh_token.payload)
    assert 1 == len(RefreshToken.objects.all())
    response = make_request({"refresh_token": refresh_token.encoded})
    assert 204 == response.status_code
    assert 0 == len(RefreshToken.objects.all())

    # now the refresh token is invalid
    response = make_request({"refresh_token": refresh_token.encoded})
    assert 400 == response.status_code
    assert b"token is invalid" in response.content


def make_request(data):
    client = Client()
    url = reverse(revoke_refresh_token)
    return client.delete(url, data, content_type="application/json")
