#!/bin/bash

set -eux

cd /app

AUTOMIGRATE=${AUTOMIGRATE:-yes}
NUM_WORKERS_DEFAULT=$((2 * $(nproc --all)))
export NUM_WORKERS=${NUM_WORKERS:-$NUM_WORKERS_DEFAULT}

if [ "$AUTOMIGRATE" != "skip" ]; then
  nf migrate --noinput
fi

exec gunicorn notfellchen.wsgi \
    --name notfellchen \
    --workers $NUM_WORKERS \
    --max-requests 1200 \
    --max-requests-jitter 50 \
    --log-level=info \
    --bind 0.0.0.0:7345

