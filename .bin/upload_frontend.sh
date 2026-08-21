#!/bin/bash

set -euo pipefail

DIR=$(dirname $BASH_SOURCE)
ROOT_DIR="$(realpath "$(dirname "$0")/..")"
source $DIR/utils.sh
load_env

# Run vite build
cd frontend
pnpm vite build

S3_BUILD_BUCKET_NAME=ctfng-builds
RELEASE=$(get_current_commit)

echo $S3_BUILD_BUCKET_NAME
echo $RELEASE

AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY aws s3 sync "$ROOT_DIR/frontend/dist/$RELEASE" "s3://$S3_BUILD_BUCKET_NAME/$RELEASE/" \
  --exclude "*.map" \
  --content-disposition "inline" \
  --storage-class ONEZONE_IA \
  --delete
