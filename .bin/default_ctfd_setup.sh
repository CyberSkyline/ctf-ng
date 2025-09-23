#!/bin/bash

set -euo pipefail

DIR=$(dirname $BASH_SOURCE)
source $DIR/utils.sh

check_ctfd_running

highlight "THIS WILL DELETE THE EXISTING DATABASE AND INSERT SAMPLE DATA\n"

prompt_user "Are you sure you want to continue?" && {
  docker exec ng-ctfd /bin/bash -c "PYTHONPATH=/opt/CTFd/ SCRIPT=true /opt/CTFd/CTFd/plugins/ng/scripts/default_ctfd_setup.py"
}