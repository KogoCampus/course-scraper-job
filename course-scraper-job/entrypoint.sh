#!/bin/bash
set -e

# Start Celery worker with beat in background
celery -A celery_app worker --beat --loglevel=info &

# Start Flower in background
celery -A celery_app flower --port=5555 --address=0.0.0.0 &

# Wait for any process to exit
wait -n

# Exit with status of process that exited first
exit $? 