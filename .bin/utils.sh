#!/bin/bash

set -euo pipefail

SCRIPT_DIR=$(dirname $BASH_SOURCE)
ENV_PATH=$(realpath "$SCRIPT_DIR/../.env")

prompt_user() {
  # Scripts can set ASSUME_YES=true (e.g. after parsing a --yes flag) to skip this prompt.
  if [[ "${ASSUME_YES:-false}" == "true" ]]; then
    return 0
  fi

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

ctfd_exec() {
  local container="$1"
  shift
  if docker exec "$container" test -f /opt/CTFd/conf/ctfd/init_secrets.py; then # don't try to get secrets in dev
    docker exec "$container" /bin/bash -c "eval \"\$(python3 /opt/CTFd/conf/ctfd/init_secrets.py)\" && $*"
  else
    docker exec "$container" /bin/bash -c "$*"
  fi
}

check_ctfd_running() {
  local container_name=$(docker ps --format '{{.Names}}' | grep -E 'ng-ctfd|ng_ctfd' | head -n 1)
  
  if [ -z "$container_name" ]; then
    highlight "The CTFd container is not running. Please run 'pnpm start' to start the container in dev or check if your host has a running CTFng instance\n" >&2
    exit 1
  fi
  echo "$container_name"
}
with_aws_creds() {
  if [[ -n "${AWS_ACCESS_KEY_ID:-}" && "$AWS_ACCESS_KEY_ID" != "-" ]]; then
    AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN= "$@"
  else
    "$@"
  fi
}

get_current_commit() {
  git log --no-color -n 1 --pretty=format:%H | tr -d '[:space:]'
}

isSwarmNode() {
  if ! command -v docker &> /dev/null; then
    echo "Docker is not installed."
    exit 1
  fi

  echo "Checking if this node is part of a Docker Swarm..."
  if [ "$(docker info | grep Swarm | sed 's/Swarm: //g')" == "inactive" ]; then
      return 1
  else
      return 0
  fi
}
