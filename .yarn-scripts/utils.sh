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
