import pytest

from ..models.user import User
from .user_layer import get_or_create_user, set_user_as_active, set_user_as_inactive


def assert_rows_in_db(expected):
    assert expected == len(User.objects.all())


@pytest.fixture
def user():
    user, _ = get_or_create_user("test-user", "+447101010101")
    return user


@pytest.mark.django_db(transaction=True)
def test_get_or_create_user():
    assert_rows_in_db(0)
    user_1, created = get_or_create_user("+447000000000")
    assert_rows_in_db(1)
    assert True is created
    assert "+447000000000" == user_1.phone_number
    assert "gatekeeper:" in user_1.user_id

    user_2, created = get_or_create_user("+447000000000")
    assert False is created
    assert user_1 == user_2
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
