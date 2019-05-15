from django.urls import path

from .views import send_verification_code, verify_phone_number

urlpatterns = [
    path("v1/send-verification-code/", send_verification_code.send_verification_code),
    path("v1/verify-phone-number/", verify_phone_number.verify_phone_number),
]
