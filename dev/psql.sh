#!/bin/bash

set -eu

docker-compose exec -u postgres db psql "$@"
