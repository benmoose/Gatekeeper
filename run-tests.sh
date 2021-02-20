#!/bin/bash

export ENVIRONMENT=test
export DJANGO_SETTINGS_MODULE=django_conf.settings

export TWILIO_ACCOUNT_SID=test-account-sid
export TWILIO_AUTH_TOKEN=test-auth-token
export TWILIO_MESSAGING_SERVICE_SID=test-messaging-service-sid

pytest --pyargs "$@"
