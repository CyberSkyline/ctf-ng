#!/bin/bash

set -euo pipefail

DIR=$(dirname $BASH_SOURCE)
source $DIR/utils.sh

CTFD_CONTAINER=$(check_ctfd_running)
echo "Found CTFd container '$CTFD_CONTAINER'"

# ctfd_exec runs the command through bash -c, so each argument is quoted to keep names with spaces intact
ARGS=""
for arg in "$@"; do
	ARGS="$ARGS $(printf '%q' "$arg")"
done

ctfd_exec $CTFD_CONTAINER "PYTHONPATH=/opt/CTFd/ SCRIPT=true python3 /opt/CTFd/CTFd/plugins/ng/scripts/event_cleanup.py$ARGS"
