#!/bin/bash

# App Runner service information
SERVICE_ARN="arn:aws:apprunner:us-west-2:992382730467:service/production-course-scraper-job/96dd40bb20604e3dadc5221a22981449"
REGION="us-west-2"

# Function to check App Runner service status
check_service_status() {
    echo "Checking App Runner service status for: $SERVICE_ARN"

    STATUS=$(aws apprunner describe-service \
        --service-arn "$SERVICE_ARN" \
        --region "$REGION" \
        --query 'Service.Status' \
        --output text)

    echo "Current App Runner service status: $STATUS"

    if [[ "$STATUS" != "RUNNING" && "$STATUS" != "OPERATION_IN_PROGRESS" ]]; then
        echo "Service is not in a deployable state. Current status: $STATUS"
        exit 1
    elif [[ "$STATUS" == "OPERATION_IN_PROGRESS" ]]; then
        echo "A deployment is already in progress. Exiting."
        exit 1
    fi
}

# Function to trigger the App Runner deployment
trigger_deploy() {
    echo "Triggering App Runner deployment for service: $SERVICE_ARN"

    aws apprunner start-deployment \
        --service-arn "$SERVICE_ARN" \
        --region "$REGION"

    if [ $? -eq 0 ]; then
        echo "Deployment successfully triggered."
    else
        echo "Failed to trigger deployment."
        exit 1
    fi
}

# Main execution
check_service_status
trigger_deploy
