class BaseProvider:
    @classmethod
    def get_provider(cls):
        raise NotImplementedError

    def get_provider_id(self):
        raise NotImplementedError

    def send_sms(self, to_number: str, message: str, status_callback: str) -> bool:
        raise NotImplementedError
