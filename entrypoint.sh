#!/bin/bash
set -e

# Source environment variables
source .env

# Start Celery worker with beat in background
celery -A celery_app worker --beat --loglevel=info &

# Configure Flower based on environment
if [ "$ENV" = "production" ]; then
    # Production mode with OAuth
    celery -A celery_app flower \
        --port=5555 \
        --address=0.0.0.0 \
        --logging=INFO \
        --auth_provider="$FLOWER_AUTH_PROVIDER" \
        --oauth2_key="$FLOWER_OAUTH2_KEY" \
        --oauth2_secret="$FLOWER_OAUTH2_SECRET" \
        --oauth2_redirect_uri="$FLOWER_OAUTH2_REDIRECT_URI" &
else
    # Development mode without authentication
    export FLOWER_UNAUTHENTICATED_API=true
    celery -A celery_app flower \
        --port=5555 \
        --address=0.0.0.0 \
        --logging=INFO &
fi

# Wait for any process to exit
wait -n

# Exit with status of process that exited first
exit $? 