#!/bin/bash
set -e

# Source and export environment variables
set -a  # automatically export all variables
source .env
set +a

# Start Celery worker with beat in background
celery -A celery_app worker --beat --loglevel=info &

# Use the full filename with .py extension
celery -A celery_app flower --conf=flowerconfig.py &

# Wait for any process to exit
wait -n

# Exit with status of process that exited first
exit $? 