#!/bin/bash

# This script syncs /usr/mnt/keys with the contents of S3 bucket S3_KEYS_BUCKET
# every 60 seconds.

set -e

echo "** Sync Keys Entrypoint **"

[[ -z ${S3_KEYS_BUCKET} ]] && echo "Missing S3_KEYS_BUCKET environment variable" && exit 1

mkdir -p /usr/mnt/keys

while true; do
    echo -n "Syncing with bucket '${S3_KEYS_BUCKET}' at "$(date -u)"... "
    touch .last-updated
    if aws s3 sync s3://${S3_KEYS_BUCKET} /usr/mnt/keys --exact-timestamps --delete; then
        echo "Done!"
    fi
    sleep 60
done
