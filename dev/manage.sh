#!/bin/bash

set -eu

docker-compose run --rm --entrypoint ./gatekeeper/manage.py server "$@"
