#!/bin/bash
set -e

# Source environment variables
source .env

# Start Celery worker with beat in background
celery -A celery_app worker --beat --loglevel=info &

celery -A celery_app flower --conf=flowerconfig &

# Wait for any process to exit
wait -n

# Exit with status of process that exited first
exit $? 