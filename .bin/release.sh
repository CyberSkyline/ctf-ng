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

if [[ -n "$(git status --porcelain)" ]]; then
  echo "Working tree has uncommitted or untracked changes and must be cleaned up before a release"
  git status --short
  exit 1
fi

RELEASE=$(get_current_commit)
APP_IMAGE="$ECR_REGISTRY/ctf-ng/app/$ENVIRONMENT:$RELEASE"
NGINX_IMAGE="$ECR_REGISTRY/ctf-ng/nginx/$ENVIRONMENT:$RELEASE"

echo "Releasing $RELEASE for $ENVIRONMENT"

# Build and push the ctfd image
docker build -t "$APP_IMAGE" -f "$ROOT_DIR/dockerfiles/ctfd.Dockerfile" "$ROOT_DIR"
docker push "$APP_IMAGE"

# Build the frontend, then build and push the nginx image with it baked in
(cd "$ROOT_DIR/frontend" && pnpm vite build)
docker build -t "$NGINX_IMAGE" -f "$ROOT_DIR/dockerfiles/nginx.Dockerfile" "$ROOT_DIR"
docker push "$NGINX_IMAGE"

echo "Released $RELEASE for $ENVIRONMENT"
