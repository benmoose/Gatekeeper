#!/bin/bash

set -e

echo "** Django Entrypoint **"
echo "ENVIRONMENT: ${ENVIRONMENT}"
echo "DJANGO_SETTINGS_MODULE: ${DJANGO_SETTINGS_MODULE}"

mkdir -p /var/tmp/shared-mount

# this may need a rethink when multiple servers are running... what if we remove columns?
./gatekeeper/manage.py migrate --no-input

exec gunicorn -w 1 \
    --threads 1 \
    --timeout 240 \
    --name gatekeeper \
    --log-level info \
    --pid /var/run/app.pid \
    --bind unix:/var/tmp/shared-mount/gunicorn.sock \
    --error-logfile - \
    --access-logfile - \
    --capture-output \
    --chdir gatekeeper \
    "django_conf.wsgi:application"
