import pytest

from ..models.user import User
from .user_layer import get_or_create_user, set_user_as_active, set_user_as_inactive


@pytest.fixture
def user():
    user, _ = get_or_create_user("+447101010101")
    return user


@pytest.mark.django_db(transaction=True)
def test_get_or_create_user():
    user_1, created = get_or_create_user("+447000000000")
    assert 1 == User.objects.all().count()
    assert True is created
    assert "+447000000000" == user_1.phone_number

    user_2, created = get_or_create_user("+447000000000")
    assert False is created
    assert user_1 == user_2
    assert 1 == User.objects.all().count()


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
