#!/bin/bash

set -e

if [[ $1 == "--check" ]]; then
    echo "Checking code..."
    black --check . && isort -rc -q gatekeeper --check-only
else
    echo "Linting code..."
    black . && isort -rc -q gatekeeper
fi
