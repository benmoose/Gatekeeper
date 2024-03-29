from .base_provider import BaseProvider

MOCK_PROVIDER_ID = "mock-provider"


class MockProvider(BaseProvider):
    def __init__(self):
        self.send_sms_attempts = []
        self.should_succeed = True

    @classmethod
    def get_provider(cls) -> "MockProvider":
        return MOCK_PROVIDER

    def get_provider_id(self) -> str:
        return MOCK_PROVIDER_ID

    def send_sms(self, to_number: str, message: str, status_callback: str) -> bool:
        self.send_sms_attempts.append((to_number, message, status_callback))
        return self.should_succeed

    def start_failing(self):
        self.should_succeed = False

    def stop_failing(self):
        self.should_succeed = True

    def reset(self):
        self.send_sms_attempts = []
        self.should_succeed = True


MOCK_PROVIDER = MockProvider()


def reset_mock_provider():
    global MOCK_PROVIDER
    MOCK_PROVIDER = MockProvider()
