from django.urls import path

from .views import (
    health,
    retrieve_access_token,
    revoke_refresh_token,
    send_verification_code,
    verify_phone_number,
)

urlpatterns = [
    path("v1/health/", health.health),
    path("v1/send-verification-code/", send_verification_code.send_verification_code),
    path("v1/verify-phone-number/", verify_phone_number.verify_phone_number),
    path("v1/access-token/", retrieve_access_token.retrieve_access_token),
    path("v1/refresh-token/", revoke_refresh_token.revoke_refresh_token),
]
