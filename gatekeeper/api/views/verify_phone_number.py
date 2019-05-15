from typing import Optional

from django.views.decorators.http import require_POST

from common.model import data_model
from common.response import error_response, success_response
from common.time import get_current_utc_time
from db.user import create_user
from db.verification import get_active_verification_codes_for_phone_number

from ..models.user import User


@data_model
class RequestData:
    phone_number: str
    verification_code: str


@require_POST
def verify_phone_number(request):
    request_data = get_request_data(request.POST)
    if request_data is None:
        return error_response("missing or invalid data")

    current_time = get_current_utc_time()
    active_codes = get_active_verification_codes_for_phone_number(
        request_data.phone_number, current_time
    )
    is_valid_code = request_data.verification_code in active_codes
    if not is_valid_code:
        return error_response("invalid verification code")

    user = create_user(phone_number=request_data.phone_number)
    return success_response(User.from_db_model(user))


def get_request_data(request_body: dict) -> Optional[RequestData]:
    try:
        return RequestData.from_dict(request_body)
    except Exception:  # noqa
        return None
