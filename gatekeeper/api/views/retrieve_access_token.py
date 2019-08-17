from datetime import datetime
from typing import Optional

from django.views.decorators.http import require_POST

from common.jwt import generate_access_token_for_user
from common.model import data_model
from common.parse import safe_parse_json
from common.response import error_response, success_response
from common.time import from_timestamp, get_current_utc_time

from ..utils.refresh_token import get_refresh_token_payload_if_active


@data_model
class RequestData:
    refresh_token: str


@data_model
class ResponseData:
    access_token: str
    expiry_time: datetime


@require_POST
def retrieve_access_token(request):
    """
    Generates and returns a new access token, given a valid refresh token.
    """
    request_data = get_request_data(request.body)
    if request_data is None:
        return error_response("Invalid or missing fields in request body")

    refresh_token_payload = get_refresh_token_payload_if_active(
        request_data.refresh_token
    )
    if refresh_token_payload is None:
        return error_response("Refresh token is invalid")

    current_time = get_current_utc_time()
    access_token, access_token_payload = generate_access_token_for_user(
        refresh_token_payload["sub"], current_time
    )
    response_data = ResponseData(
        access_token=access_token,
        expiry_time=from_timestamp(access_token_payload["exp"]),
    )
    return success_response(response_data)


def get_request_data(request_body: str) -> Optional[RequestData]:
    try:
        return RequestData.from_dict(safe_parse_json(request_body))
    except Exception:
        return None
