#!/bin/bash

set -euo pipefail

SCRIPT_DIR=$(dirname $BASH_SOURCE)
ENV_PATH=$(realpath "$SCRIPT_DIR/../.env")

prompt_user() {
  local message="\033[1;33m$1\033[0m"
  echo -ne "$message"
  read -p " (y/n): " response
  if [[ "$response" == "y" || "$response" == "Y" ]]; then
    return 0
  else
    return 1
  fi
}

user_input() {
  read -p ": " response
  echo "$response"
}

highlight() {
  echo -ne "\033[1;33m$1\033[0m"
}

load_env() {
  if [[ ! -f "$ENV_PATH" ]]; then
    highlight "Error: .env file not found at $ENV_PATH\n"
    exit 1
  fi

  source $ENV_PATH
}

check_ctfd_running() {
  local container_name=$(docker ps --format '{{.Names}}' | grep -E '^ng-ctfd$|ng_ctfd')
  
  if [ -z "$container_name" ]; then
    highlight "The CTFd container is not running. Please run 'pnpm start' to start the container\n" >&2
    exit 1
  fi
  echo "$container_name"
}

get_current_commit() {
  git log --no-color -n 1 --pretty=format:%H | tr -d '[:space:]'
}