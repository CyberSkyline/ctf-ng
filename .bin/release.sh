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

case "$ENVIRONMENT" in
  staging) ENV_PREFIX="stg" ;;
  production) ENV_PREFIX="prod" ;;
esac

echo "Releasing $RELEASE for $ENVIRONMENT"

# Build and push the ctfd image
docker build -t "$APP_IMAGE" -f "$ROOT_DIR/dockerfiles/ctfd.Dockerfile" "$ROOT_DIR"
docker push "$APP_IMAGE"

# Build the frontend, then build and push the nginx image with it baked in
(cd "$ROOT_DIR/frontend" && pnpm vite build)
docker build -t "$NGINX_IMAGE" -f "$ROOT_DIR/dockerfiles/nginx.Dockerfile" "$ROOT_DIR"
docker push "$NGINX_IMAGE"

echo "Released $RELEASE for $ENVIRONMENT"

# Mirror the version pinned to this commit on development (tagged v* by the
# semver workflow), falling back to a patch bump of this env's last version.
git fetch origin --tags --quiet
VERSION=$(git describe --tags --match 'v*' --abbrev=0 "$RELEASE" 2>/dev/null || true)
if [[ -z "$VERSION" ]]; then
  # Check for old tags
  LEGACY=$(git describe --tags --match 'dev-v*' --abbrev=0 "$RELEASE" 2>/dev/null || true)
  VERSION="${LEGACY#dev-}"
fi
if [[ -z "$VERSION" ]]; then
  LATEST=$(git tag --list "${ENV_PREFIX}-v*" --sort=-v:refname | head -n1)
  IFS='.' read -r MAJOR MINOR PATCH <<< "${LATEST#${ENV_PREFIX}-v}"
  VERSION="v${MAJOR:-0}.${MINOR:-0}.$(( ${PATCH:-0} + 1 ))"
fi

NEW_TAG="${ENV_PREFIX}-${VERSION}"
if ! git rev-parse "$NEW_TAG" >/dev/null 2>&1; then
  git tag -a "$NEW_TAG" "$RELEASE" -m "Release $NEW_TAG ($ENVIRONMENT) for commit $RELEASE"
  git push origin "$NEW_TAG"
  echo "Tagged $RELEASE as $NEW_TAG"
fi
