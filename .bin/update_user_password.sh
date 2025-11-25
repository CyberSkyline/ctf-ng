#!/bin/bash

set -euo pipefail

DIR=$(dirname $BASH_SOURCE)
source $DIR/utils.sh

USER_EMAIL="${1:-}"

if [[ -z "${USER_EMAIL:-}" ]]; then
	echo "Usage: $0 <user_email>"
	exit 1
fi

echo -n "Enter password for $USER_EMAIL: "
read -s USER_PASSWORD
echo  # Add newline after hidden input

if [[ -z "${USER_PASSWORD:-}" ]]; then
	echo "Error: Password cannot be empty"
	exit 1
fi

CTFD_CONTAINER=$(check_ctfd_running)
echo "Found CTFd container '$CTFD_CONTAINER'"

prompt_user "Are you sure you want to continue?" && {
  docker exec $CTFD_CONTAINER /bin/bash -c "PYTHONPATH=/opt/CTFd/ SCRIPT=true /opt/CTFd/CTFd/plugins/ng/scripts/update_user_password.py $USER_EMAIL $USER_PASSWORD"
}
