from datetime import datetime, timedelta

import pytest
import pytz
from django.db import IntegrityError

from ..models.verification_code import VerificationCode
from .verification_code_layer import (
    create_verification_code,
    get_active_verification_codes_for_phone_number,
    invalidate_verification_code,
)


@pytest.fixture
def expiry_time():
    return datetime(2019, 1, 1, tzinfo=pytz.UTC)


@pytest.mark.django_db
def test_create_verification_code(expiry_time):
    assert 0 == len(VerificationCode.objects.all())
    verification_code = create_verification_code("+447000000000", "abcd", expiry_time)
    assert 1 == len(VerificationCode.objects.all())
    assert "+447000000000" == verification_code.phone_number
    assert "abcd" == verification_code.code
    assert expiry_time == verification_code.expires_at


@pytest.mark.django_db
def test_create_verification_code_unique_codes(expiry_time):
    create_verification_code("+447000000000", "abcd", expiry_time)
    with pytest.raises(IntegrityError):
        create_verification_code("+447000000001", "abcd", expiry_time)


@pytest.mark.django_db
def test_create_verification_code_duplicate_phone_numbers_allowed(expiry_time):
    create_verification_code("+447000000000", "abcd", expiry_time)
    create_verification_code("+447000000000", "abcde", expiry_time)


@pytest.mark.django_db
def test_get_active_verification_codes():
    time_now = datetime(2019, 1, 1, tzinfo=pytz.UTC)
    create_verification_code("+447000000000", "a", time_now - timedelta(minutes=1))
    create_verification_code("+447000000000", "b", time_now)
    create_verification_code("+447000000000", "c", time_now + timedelta(minutes=1))
    code_inactive = create_verification_code(
        "+447000000000", "d", time_now + timedelta(minutes=1)
    )
    invalidate_verification_code(code_inactive)

    assert ["c"] == get_active_verification_codes_for_phone_number(
        "+447000000000", time_now
    )


@pytest.mark.django_db
def test_invalidate_verification_code(expiry_time):
    verification_code = create_verification_code("+447000000000", "abcd", expiry_time)
    assert verification_code.is_active

    invalidate_verification_code(verification_code)
    verification_code.refresh_from_db()
    assert False is verification_code.is_active
