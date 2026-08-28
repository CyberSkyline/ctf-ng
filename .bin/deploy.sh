#!/bin/bash

set -euo pipefail

DIR=$(dirname $BASH_SOURCE)
ROOT_DIR="$(realpath "$(dirname "$0")/..")"
source $DIR/utils.sh
load_env

if [[ -z "${ECR_REGISTRY:-}" || "$ECR_REGISTRY" == "-" ]]; then
  echo "Error: ECR_REGISTRY must be set in your .env"
  exit 1
fi

if [[ -z "${CTFD_ENVIRONMENT:-}" || "$CTFD_ENVIRONMENT" == "-" ]]; then
  echo "Error: CTFD_ENVIRONMENT must be set in your .env"
  exit 1
fi

cd "$ROOT_DIR"

# Optional arg for convenient rollbacks as necessary; can specify a commit hash and run deploy process with that image/frontend version instead
RELEASED_SHA="${1:-}"
if [[ -z "$RELEASED_SHA" ]]; then
  RELEASED_SHA=$(AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION \
    aws ecr describe-images --repository-name "ctf-ng/app/$CTFD_ENVIRONMENT" \
    --query "sort_by(imageDetails,&imagePushedAt)[-1].imageTags[0]" --output text)
fi

echo "Deploying $RELEASED_SHA for $CTFD_ENVIRONMENT"

git fetch origin
git checkout "$RELEASED_SHA"

pnpm update-commit-env
pnpm download-frontend

docker pull "$ECR_REGISTRY/ctf-ng/app/$CTFD_ENVIRONMENT:$RELEASED_SHA"

# Persisted for `pnpm kick-stack` (a plain restart, no new release lookup)
sed -i "/^CTFD_TAG=/d" .env
echo "CTFD_TAG=$RELEASED_SHA" >> .env

ECR_REGISTRY=$ECR_REGISTRY CTFD_ENVIRONMENT=$CTFD_ENVIRONMENT CTFD_TAG=$RELEASED_SHA \
  docker stack deploy -c docker-compose.prod.yaml ctf-ng

echo "Deployed $RELEASED_SHA for $CTFD_ENVIRONMENT"
