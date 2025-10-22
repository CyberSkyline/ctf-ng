#!/bin/bash

# Checks for fields in `conf/.env.default` that are not present in `.env` and copies over the default values for any missing fields

set -euo pipefail

DIR=$(dirname $BASH_SOURCE)
source $DIR/utils.sh

ENV_PATH=$(realpath "$DIR/../.env")
DEV_ENV_PATH=$(realpath "$DIR/../.env.dev")
PROD_ENV_PATH=$(realpath "$DIR/../.env.prod")

DEFAULT_ENV_PATH=$(realpath "$DIR/../conf/.env.default")
DEFAULT_DEV_ENV_PATH=$(realpath "$DIR/../conf/ctfd/.env.default.dev")
DEFAULT_PROD_ENV_PATH=$(realpath "$DIR/../conf/ctfd/.env.default.prod")

sync_values () {
  local_env_file="$1"
  default_env_file="$2"

  # Ensure both files exist
  if [[ ! -f "$local_env_file" ]]; then
    touch "$local_env_file"
  fi

  # Read file line by line, handling the last line even if it lacks a newline
  while IFS= read -r line || [[ -n "$line" ]]; do
    # Ignore empty lines and comments
    [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]] && continue
    # Only process lines with variable assignments (VAR=VAL)
    if [[ "$line" =~ ^[[:space:]]*([A-Za-z_][A-Za-z0-9_]*)= ]]; then
      var_name="${BASH_REMATCH[1]}"
      # Check if variable exists in local env file
      if ! grep -qE "^[[:space:]]*${var_name}=" "$local_env_file"; then
        echo "$line" >> "$local_env_file"
      fi
    fi
  done < "$default_env_file"
}

sync_values $ENV_PATH $DEFAULT_ENV_PATH
sync_values $DEV_ENV_PATH $DEFAULT_DEV_ENV_PATH
sync_values $PROD_ENV_PATH $DEFAULT_PROD_ENV_PATH