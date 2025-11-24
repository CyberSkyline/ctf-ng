#!/bin/bash

set -euo pipefail

DIR=$(dirname $BASH_SOURCE)
source $DIR/utils.sh

PROD_ENV_PATH=$(realpath "$DIR/../.env.prod")

COMMIT_HASH=$(git rev-parse HEAD)
STATIC_BUILD_PATH="/dist/$COMMIT_HASH"

# Update the STATIC_BUILD_PATH in the .env file using sed
sed -i "s|^STATIC_BUILD_PATH=.*|STATIC_BUILD_PATH=$STATIC_BUILD_PATH|" "$PROD_ENV_PATH"
