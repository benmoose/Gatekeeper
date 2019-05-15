#!/bin/bash

set -eu

docker-compose run --rm --no-deps --entrypoint ./run-linter.sh server "$@"
