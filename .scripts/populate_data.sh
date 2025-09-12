#!/bin/bash

set -euo pipefail

DIR=$(dirname $BASH_SOURCE)
source $DIR/utils.sh

check_ctfd_running

echo -e "\e[43m\e[30mTHIS WILL DELETE THE EXISTING DATABASE AND INSERT SAMPLE DATA\e[0m"
prompt_user "Are you sure you want to continue?" && {
  docker exec ng-ctfd /bin/bash -c "PYTHONPATH=/opt/CTFd/ SCRIPT=true /opt/CTFd/CTFd/plugins/ng/scripts/populate_sample_data.py"
}