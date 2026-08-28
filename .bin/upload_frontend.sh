#!/bin/bash

set -euo pipefail

DIR=$(dirname $BASH_SOURCE)
source $DIR/utils.sh
load_env

with_aws_creds "$DIR/build_and_upload_frontend.sh"
