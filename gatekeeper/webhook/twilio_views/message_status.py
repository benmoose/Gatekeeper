import logging
from typing import Optional

from django.views.decorators.http import require_POST

from common.response import error_response, success_response

from ..models.twilio_webhook_request import TwilioSMSWebhookRequest

logger = logging.getLogger(__name__)


@require_POST
def message_status_webhook(request):
    request_data = get_request_data(request.POST)
    if request_data is None:
        logger.error("got invalid webhook request")
        return error_response()

    logger.info(f"message status updated: {request_data}")
    return success_response()


def get_request_data(data: dict) -> Optional[TwilioSMSWebhookRequest]:
    try:
        return TwilioSMSWebhookRequest.from_dict(data)
    except KeyError:
        return None
