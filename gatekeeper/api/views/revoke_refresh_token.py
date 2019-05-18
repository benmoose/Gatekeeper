import logging
from typing import Optional

from django.views.decorators.http import require_http_methods

from common.jwt import decode_token
from common.model import data_model
from common.parse import safe_parse_json
from common.response import error_response, success_response
from db.tokens import delete_refresh_token

from ..utils.refresh_token import get_refresh_token_payload_if_active

logger = logging.getLogger(__name__)


@data_model
class RequestData:
    refresh_token: str


@require_http_methods(["DELETE"])
def revoke_refresh_token(request):
    request_data = get_request_data(request.body)
    if request_data is None:
        return error_response("Invalid or malformed request data")

    payload = get_refresh_token_payload_if_active(request_data.refresh_token)
    if payload is None:
        return error_response("Refresh token is invalid")

    success = delete_refresh_token(token_id=payload["jti"])
    if not success:
        logger.info(
            f"Attempt to delete non-existent token: sub={payload['sub']}, jti={payload['jti']}"
        )

    return success_response(status=204)


def get_request_data(request_body: str) -> Optional[RequestData]:
    try:
        return RequestData.from_dict(safe_parse_json(request_body))
    except Exception:
        return None
