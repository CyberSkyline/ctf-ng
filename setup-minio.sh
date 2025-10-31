#!/bin/bash
# setup-minio.sh - Initialize MinIO bucket for local development

set -e

echo ""
echo "MinIO Setup for CTFd Development"
echo ""

# Load configuration from environment file
ENV_FILE="${ENV_FILE:-.env.dev}"
CTFD_ENV_FILE="conf/ctfd/${ENV_FILE}"

# Source environment variables if file exists
if [ -f "$CTFD_ENV_FILE" ]; then
    echo "Loading configuration from $CTFD_ENV_FILE"
    set -a
    source "$CTFD_ENV_FILE"
    set +a
elif [ -f "conf/ctfd/.env.default.dev" ]; then
    echo "Loading configuration from conf/ctfd/.env.default.dev"
    set -a
    source "conf/ctfd/.env.default.dev"
    set +a
else
    echo "Warning: No environment file found, using defaults"
fi

MINIO_CONTAINER="ng-minio"
# Use environment variables with defaults
BUCKET_NAME="${MINIO_BUCKET:-ctfd-attachments}"
MINIO_ENDPOINT="${MINIO_ENDPOINT:-http://localhost:9000}"
MINIO_USER="${MINIO_ACCESS_KEY:-minioadmin}"
MINIO_PASSWORD="${MINIO_SECRET_KEY:-minioadmin}"

echo "Checking MinIO container status..."
if ! docker ps | grep -q "$MINIO_CONTAINER"; then
    echo ""
    echo "MinIO container is not running"
    echo ""
    echo "Please start MinIO first:"
    echo "  docker compose up -d minio"
    echo ""
    echo "Or run the full development environment:"
    echo "  npm start"
    echo ""
    exit 1
fi

echo "MinIO container is running"
echo ""

echo "Waiting for MinIO API to be ready..."
for i in {1..30}; do
    if docker exec "$MINIO_CONTAINER" mc alias set local "$MINIO_ENDPOINT" "$MINIO_USER" "$MINIO_PASSWORD" 2>/dev/null; then
        echo "MinIO API is ready"
        break
    fi
    if [ $i -eq 30 ]; then
        echo ""
        echo "MinIO failed to start within 30 seconds"
        echo ""
        echo "Try restarting MinIO:"
        echo "docker compose restart minio"
        echo ""
        exit 1
    fi
    sleep 1
done

echo ""

echo "Checking if bucket exists..."
if docker exec "$MINIO_CONTAINER" mc ls local 2>/dev/null | grep -q "$BUCKET_NAME"; then
    echo "Bucket '$BUCKET_NAME' already exists"
else
    echo "Creating bucket '$BUCKET_NAME'..."
    docker exec "$MINIO_CONTAINER" mc mb "local/$BUCKET_NAME"
    echo "Bucket created successfully"
fi

echo ""

echo "Configuring bucket policy..."
docker exec "$MINIO_CONTAINER" mc anonymous set download "local/$BUCKET_NAME" 2>/dev/null
echo "Bucket policy set to public"

echo ""
echo "MinIO Setup Complete :) "
echo ""
echo "MinIO Web Console: http://localhost:9001"
echo "   Username: $MINIO_USER"
echo "   Password: $MINIO_PASSWORD"
echo ""
echo "Bucket: $BUCKET_NAME"
echo ""
echo "Next steps:"
echo "  1. npm start"
echo "  2. Upload test image to verify setup"
echo ""
