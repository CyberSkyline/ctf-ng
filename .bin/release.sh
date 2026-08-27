#!/bin/bash

set -euo pipefail

DIR=$(dirname $BASH_SOURCE)
ROOT_DIR="$(realpath "$(dirname "$0")/..")"
source $DIR/utils.sh
load_env

ENVIRONMENT="${1:-}"
if [[ "$ENVIRONMENT" != "staging" && "$ENVIRONMENT" != "production" ]]; then
  echo "Usage: $0 <staging|production>"
  exit 1
fi

if [[ -z "${ECR_REGISTRY:-}" || "$ECR_REGISTRY" == "-" ]]; then
  echo "Error: ECR_REGISTRY must be set in your .env"
  exit 1
fi

RELEASE=$(get_current_commit)
IMAGE="$ECR_REGISTRY/ctf-ng/app/$ENVIRONMENT:$RELEASE"

echo "Releasing $RELEASE for $ENVIRONMENT"

# Log in to ECR using the static key in .env
AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION \
  aws ecr get-login-password | docker login --username AWS --password-stdin "$ECR_REGISTRY"

# Build and push the ctfd image
docker build -t "$IMAGE" -f "$ROOT_DIR/dockerfiles/ctfd.Dockerfile" "$ROOT_DIR"
docker push "$IMAGE"

# Build and upload the frontend
cd "$ROOT_DIR/frontend"
pnpm vite build
cd "$ROOT_DIR"

AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY aws s3 sync "$ROOT_DIR/frontend/dist/$RELEASE" "s3://ctfng-builds/$RELEASE/" \
  --exclude "*.map" \
  --content-disposition "inline" \
  --storage-class ONEZONE_IA \
  --delete

echo "Released $RELEASE for $ENVIRONMENT"
