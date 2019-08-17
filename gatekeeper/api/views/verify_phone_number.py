import logging
from datetime import datetime
from typing import Optional

from django.views.decorators.http import require_POST

from common.jwt import (
    generate_access_token_for_user,
    generate_refresh_token_for_user,
    generate_refresh_token_id,
)
from common.model import data_model
from common.parse import safe_parse_json
from common.response import error_response, success_response
from common.time import from_timestamp, get_current_utc_time
from db.models import User
from db.tokens import register_user_refresh_token
from db.user import get_or_create_user
from db.verification import (
    get_active_verification_codes_for_phone_number,
    invalidate_verification_code,
)

logger = logging.getLogger(__name__)


@data_model
class RequestData:
    phone_number: str
    verification_code: str


@data_model
class ResponseData:
    access_token: str
    refresh_token: str
    expiry_time: datetime


@require_POST
def verify_phone_number(request):
    """
    Given a phone number (e.164 format) and an active verification code, this endpoint
    generates a new user account capable of owning access and refresh tokens.

    An initial set of refresh and access tokens for the new account are returned on
    success.
    """
    request_data = get_request_data(request.body)
    if request_data is None:
        return error_response("Missing or invalid data")

    current_time = get_current_utc_time()
    active_codes = get_active_verification_codes_for_phone_number(
        request_data.phone_number, current_time
    )
    is_valid_code = request_data.verification_code in active_codes
    if not is_valid_code:
        return error_response("Invalid verification code")

    invalidate_verification_code(request_data.verification_code)
    user, created = get_or_create_user(phone_number=request_data.phone_number)
    if not created:
        logger.info(f"Generating refresh token for existing user {user.user_id}")

    refresh_token = generate_and_record_refresh_token(user, current_time)
    access_token, token_payload = generate_access_token_for_user(
        user.user_id, current_time
    )
    expiry_time = from_timestamp(token_payload["exp"])
    response_data = ResponseData(
        refresh_token=refresh_token, access_token=access_token, expiry_time=expiry_time
    )

    return success_response(response_data)


def get_request_data(request_body: bytes) -> Optional[RequestData]:
    try:
        return RequestData.from_dict(safe_parse_json(request_body))
    except Exception:  # noqa
        return None


def generate_and_record_refresh_token(user: User, current_time: datetime) -> str:
    token_id = generate_refresh_token_id()
    token, payload = generate_refresh_token_for_user(user, current_time, token_id)
    register_user_refresh_token(user, token_id, payload)
    return token
