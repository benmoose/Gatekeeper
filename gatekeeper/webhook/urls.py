from django.urls import path

from .twilio_views import message_status

urlpatterns = [path("message-status/", message_status.message_status_webhook)]
