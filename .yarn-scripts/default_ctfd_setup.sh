#!/bin/bash

set -euo pipefail

DIR=$(dirname $BASH_SOURCE)
source $DIR/utils.sh

if ! docker ps --format '{{.Names}}' | grep -q '^ng-ctfd$'; then
  echo "The 'ng-ctfd' container is not running. Please run 'yarn start' to start the container"
  exit 1
fi

prompt_user "Would you like to configure the default CTFd setup?" && {
  docker exec ng-ctfd /bin/bash -c "PYTHONPATH=/opt/CTFd/ SCRIPT=true /opt/CTFd/CTFd/plugins/ng/scripts/default_ctfd_setup.py"
}