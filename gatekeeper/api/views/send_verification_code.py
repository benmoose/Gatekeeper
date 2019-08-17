import logging
from datetime import datetime, timedelta
from string import digits
from typing import Iterable, Optional, Tuple

from django.conf import settings
from django.db import IntegrityError
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from phonenumbers import PhoneNumberFormat, format_number, parse

from common.generate import generate_verification_code
from common.model import data_model
from common.parse import safe_parse_json
from common.response import error_response, success_response
from common.time import get_current_utc_time
from coms.providers import get_communication_provider
from db.models import VerificationCode
from db.verification import create_verification_code, invalidate_verification_code

logger = logging.getLogger(__name__)

FIVE_MINUTES = 5 * 60

VERIFICATION_CODE_LENGTH = 4
VERIFICATION_CODE_ALPHABET = digits
VERIFICATION_CODE_LIFETIME_SECONDS = FIVE_MINUTES


@data_model
class RequestData:
    phone_number: str
    region: str


@require_POST
def send_verification_code(request) -> HttpResponse:
    request_data = get_request_data(request.body)
    if request_data is None:
        return error_response()

    phone_number = get_e164_phone_number(request_data.phone_number, request_data.region)
    if phone_number is None:
        return error_response("Invalid phone_number")

    current_time = get_current_utc_time()
    verification_code_expiry_time = current_time + timedelta(
        seconds=VERIFICATION_CODE_LIFETIME_SECONDS
    )

    provider = get_communication_provider()
    message_status_callback = settings.TWILIO_MESSAGE_STATUS_CALLBACK
    success, verification_code = send_verification_code_sms(
        provider=provider,
        phone_number=phone_number,
        verification_code_population=VERIFICATION_CODE_ALPHABET,
        verification_code_length=VERIFICATION_CODE_LENGTH,
        verification_code_expiry_time=verification_code_expiry_time,
        callback=message_status_callback,
    )
    if success is False:
        invalidate_verification_code(verification_code.code)
        return error_response("Failed to send verification SMS", status=503)

    return success_response({"phone_number": phone_number})


def get_request_data(request_body: bytes) -> Optional[RequestData]:
    try:
        return RequestData.from_dict(safe_parse_json(request_body))
    except Exception:
        return None


def get_e164_phone_number(phone_number: str, region: str) -> Optional[str]:
    """
    >>> get_e164_phone_number("+447000000000", "GB")
    '+447000000000'
    >>> get_e164_phone_number("07-000 000 00 0", "GB")
    '+447000000000'
    >>> get_e164_phone_number("07000000000", "GB")
    '+447000000000'
    >>> get_e164_phone_number("07000000000", "US")
    '+107000000000'
    >>> get_e164_phone_number("7000000000", "GB")
    '+447000000000'
    >>> get_e164_phone_number("+447a0000000b", "GB")
    '+4470000000'
    >>> get_e164_phone_number("", "GB")
    >>> get_e164_phone_number("abcdefg", "GB")
    """
    try:
        parsed_phone_number = parse(phone_number, region=region.upper())
        return format_number(parsed_phone_number, PhoneNumberFormat.E164)
    except Exception:
        return None


def send_verification_code_sms(
    provider,
    phone_number: str,
    callback: str,
    verification_code_population: Iterable,
    verification_code_length: int,
    verification_code_expiry_time: datetime,
) -> Tuple[bool, Optional[VerificationCode]]:
    """
    Attempts to send the verification SMS, whilst handling the generation of duplicate
    verification codes with retries.
    """
    verification_code = create_verification_code_with_retries(
        phone_number=phone_number,
        verification_code_population=verification_code_population,
        verification_code_length=verification_code_length,
        verification_code_expiry_time=verification_code_expiry_time,
        max_retries=5,
    )
    verification_message = get_verification_code_sms_message(verification_code.code)
    success = provider.send_sms(phone_number, verification_message, callback)
    return success, verification_code


def create_verification_code_with_retries(
    phone_number: str,
    verification_code_population: Iterable,
    verification_code_length: int,
    verification_code_expiry_time: datetime,
    max_retries: int,
) -> VerificationCode:
    for retry_count in range(max_retries):
        try:
            code = generate_verification_code(
                verification_code_population, verification_code_length
            )
            return create_verification_code(
                phone_number, code, verification_code_expiry_time
            )
        except IntegrityError:
            logger.warning(
                "Got integrity error when inserting verification code into DB, attempt"
                "%d of %d",
                retry_count + 1,
                max_retries,
            )

    raise RuntimeError(
        f"Failed to generate unique verification code after {max_retries} attempts"
    )


def get_verification_code_sms_message(verification_code: str) -> str:
    return f"Your verification code is {verification_code}"
