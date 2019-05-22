from datetime import datetime
from typing import List

from django.db import transaction

from ..models import VerificationCode


def create_verification_code(
    phone_number: str, code: str, expiry_time: datetime
) -> VerificationCode:
    return VerificationCode.objects.create(
        phone_number=phone_number, code=code, expires_at=expiry_time
    )


def get_active_verification_codes_for_phone_number(
    phone_number: str, current_time: datetime
) -> List[str]:
    return [
        verification_code.code
        for verification_code in VerificationCode.objects.filter(
            phone_number=phone_number, is_active=True, expires_at__gt=current_time
        )
    ]


@transaction.atomic
def invalidate_verification_code(code: str):
    verification_code = VerificationCode.objects.select_for_update().get(code=code)
    verification_code.is_active = False
    verification_code.save(update_fields=["is_active", "modified_on"])
