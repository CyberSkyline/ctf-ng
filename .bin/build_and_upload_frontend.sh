#!/bin/bash

# Builds the frontend and syncs it to S3 for the currently checked-out commit

set -euo pipefail

DIR=$(dirname $BASH_SOURCE)
ROOT_DIR="$(realpath "$(dirname "$0")/..")"
source $DIR/utils.sh

RELEASE=$(get_current_commit)

cd "$ROOT_DIR/frontend"
pnpm vite build
cd "$ROOT_DIR"

aws s3 sync "$ROOT_DIR/frontend/dist/$RELEASE" "s3://ctfng-builds/$RELEASE/" \
  --exclude "*.map" \
  --content-disposition "inline" \
  --storage-class ONEZONE_IA \
  --delete
