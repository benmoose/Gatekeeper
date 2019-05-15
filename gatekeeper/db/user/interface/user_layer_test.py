import pytest
from django.db import IntegrityError

from ..models.user import User
from .user_layer import get_or_create_user, set_user_as_active, set_user_as_inactive


def assert_rows_in_db(expected):
    assert expected == len(User.objects.all())


@pytest.fixture
def user():
    return get_or_create_user("test-user", "+447101010101")


@pytest.mark.django_db(transaction=True)
def test_get_or_create_user():
    assert_rows_in_db(0)
    user = get_or_create_user("+447000000000")
    assert_rows_in_db(1)
    assert "+447000000000" == user.phone_number
    assert "gatekeeper:" in user.user_id

    assert user == get_or_create_user("+447000000000")
    assert_rows_in_db(1)


@pytest.mark.django_db
def test_set_user_as_inactive(user):
    assert user.is_active
    set_user_as_inactive(user)
    user.refresh_from_db()
    assert not user.is_active

    # check idempotency
    set_user_as_inactive(user)
    user.refresh_from_db()
    assert not user.is_active


@pytest.mark.django_db
def test_set_user_as_active(user):
    user.is_active = False
    user.save()

    assert not user.is_active
    set_user_as_active(user)
    user.refresh_from_db()
    assert user.is_active

    # check idempotency
    set_user_as_active(user)
    user.refresh_from_db()
    assert user.is_active
