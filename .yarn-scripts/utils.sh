#!/bin/bash

prompt_user() {
  local message="$1"
  read -p "$message (y/n): " response
  if [[ "$response" == "y" || "$response" == "Y" ]]; then
    return 0
  else
    return 1
  fi
}

check_ctfd_running() {
  if ! docker ps --format '{{.Names}}' | grep -q '^ng-ctfd$'; then
    echo "The 'ng-ctfd' container is not running. Please run 'yarn start' to start the container"
    exit 1
  fi
}