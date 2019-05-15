from django.conf import settings

from .base_provider import BaseProvider
from .mock_provider import MockProvider
from .twilio_provider import TwilioProvider


def get_communication_provider() -> BaseProvider:
    if settings.IS_TEST_ENVIRONMENT:
        return MockProvider.get_provider()

    return TwilioProvider.get_provider()
