import logging

from django.conf import settings
from twilio.rest import Client

from .base_provider import BaseProvider

logger = logging.getLogger(__name__)

TWILIO_PROVIDER_ID = "twilio"
TWILIO_MESSAGE_OK_STATES = ["accepted", "queued", "sending", "sent", "delivered"]


class TwilioProvider(BaseProvider):
    def __init__(self, account_sid, auth_token, messaging_service_sid):
        self.twilio_client = Client(account_sid, auth_token)
        self.messaging_service_sid = messaging_service_sid

    @classmethod
    def get_provider(cls) -> "TwilioProvider":
        return cls(
            account_sid=settings.TWILIO_ACCOUNT_SID,
            auth_token=settings.TWILIO_AUTH_TOKEN,
            messaging_service_sid=settings.TWILIO_MESSAGING_SERVICE_SID,
        )

    def get_provider_id(self) -> str:
        return TWILIO_PROVIDER_ID

    def send_sms(self, to_number: str, message: str, status_callback: str) -> bool:
        last_3_digits = to_number[-3:]
        result = self.twilio_client.messages.create(
            to=to_number,
            body=message,
            status_callback=status_callback,
            messaging_service_sid=self.messaging_service_sid,
        )
        logger.info(
            f"sending verification SMS to number ending {last_3_digits}: status {result.status}"
        )
        if result.status in TWILIO_MESSAGE_OK_STATES:
            logger.warning(
                f"sending message to {last_3_digits} failed: {result.error_code} {result.error_message}"
            )

        return result.status in TWILIO_MESSAGE_OK_STATES
