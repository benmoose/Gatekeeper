from datetime import datetime
from typing import Optional

from django.views.decorators.http import require_POST

from common.jwt import (
    generate_access_token_from_refresh_token,
    generate_refresh_token_for_user,
    generate_refresh_token_id,
)
from common.model import data_model
from common.parse import safe_parse_json
from common.response import error_response, success_response
from common.time import get_current_utc_time
from db.models import User
from db.user import get_or_create_user
from db.verification import get_active_verification_codes_for_phone_number


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
    request_data = get_request_data(request.body)
    if request_data is None:
        return error_response("missing or invalid data")

    current_time = get_current_utc_time()
    active_codes = get_active_verification_codes_for_phone_number(
        request_data.phone_number, current_time
    )
    is_valid_code = request_data.verification_code in active_codes
    if not is_valid_code:
        return error_response("invalid verification code")

    current_time = get_current_utc_time()
    user = get_or_create_user(phone_number=request_data.phone_number)
    refresh_token = generate_refresh_token(user, current_time)
    access_token, expiry_time = generate_access_token_from_refresh_token(
        refresh_token, current_time
    )
    response_data = ResponseData(
        refresh_token=refresh_token, access_token=access_token, expiry_time=expiry_time
    )

    return success_response(response_data)


def get_request_data(request_body: bytes) -> Optional[RequestData]:
    try:
        return RequestData.from_dict(safe_parse_json(request_body))
    except Exception:  # noqa
        return None


def generate_refresh_token(user: User, current_time: datetime) -> str:
    refresh_token_id = generate_refresh_token_id()
    return generate_refresh_token_for_user(user, current_time, refresh_token_id)
