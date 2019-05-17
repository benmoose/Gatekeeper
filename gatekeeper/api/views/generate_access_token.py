from datetime import datetime
from typing import Optional

from common.jwt import REFRESH_TOKEN_TYPE, decode_token, generate_access_token_for_user
from common.model import data_model
from common.parse import safe_parse_json
from common.response import error_response, success_response
from common.time import from_timestamp, get_current_utc_time
from db.tokens import get_latest_refresh_token_for_user


@data_model
class RequestData:
    refresh_token: str


@data_model
class ResponseData:
    access_token: str
    expiry_time: datetime


def generate_access_token(request):
    request_data = get_request_data(request.body)
    if request_data is None:
        return error_response("Invalid or missing fields in request body")

    refresh_token_payload = get_refresh_token_payload_if_valid(
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


def get_refresh_token_payload_if_valid(refresh_token: str) -> Optional[dict]:
    """
    Return token payload if it's valid and the user's most recently issued refresh
    token.
    """
    payload = decode_token(refresh_token)
    if payload["typ"] != REFRESH_TOKEN_TYPE:
        return None
    expected_refresh_token = get_latest_refresh_token_for_user(user_id=payload["sub"])
    if expected_refresh_token is None:
        return None
    if payload["jti"] != expected_refresh_token.token_id:
        return None
    return payload
