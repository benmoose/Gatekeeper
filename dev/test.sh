#!/bin/bash

set -eu

docker-compose run --rm --entrypoint ./run-tests.sh server "$@"
