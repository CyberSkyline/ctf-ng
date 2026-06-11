#!/bin/bash

set -euo pipefail

DIR=$(dirname $BASH_SOURCE)
source $DIR/utils.sh

CTFD_CONTAINER=$(check_ctfd_running)
echo "Found CTFd container '$CTFD_CONTAINER'"

highlight "THIS WILL OVERWRITE ANY EXISTING LOAD TESTING USER INFORMATION\n"

prompt_user "Are you sure you want to continue?" && {
  ctfd_exec $CTFD_CONTAINER "PYTHONPATH=/opt/CTFd/ SCRIPT=true /opt/CTFd/CTFd/plugins/ng/scripts/populate_load_testing_data.py" \
    > $DIR/../tools/load-test/users.json
}