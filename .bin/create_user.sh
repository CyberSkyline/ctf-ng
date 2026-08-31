#!/bin/bash

set -euo pipefail

DIR=$(dirname $BASH_SOURCE)
source $DIR/utils.sh

ADMIN_FLAG=""
USER_NAME=""
USER_EMAIL=""
CSV_PATH=""

while [[ $# -gt 0 ]]; do
	case "$1" in
		--admin)
			ADMIN_FLAG="--admin"
			shift
			;;
		--name)
			if [[ -z "${2:-}" ]]; then
				echo "Error: --name requires a value"
				exit 1
			fi
			USER_NAME="$2"
			shift 2
			;;
		--csv)
			if [[ -z "${2:-}" ]]; then
				echo "Error: --csv requires a file path"
				exit 1
			fi
			CSV_PATH="$2"
			shift 2
			;;
		--yes)

			ASSUME_YES=true
			shift
			;;
		-*)
			echo "Unknown option: $1"
			echo "Usage: $0 [--admin] [--name <display_name>] [--yes] <user_email>"
			echo "       $0 [--admin] --csv <path_to_csv> [--yes]"
			exit 1
			;;
		*)
			USER_EMAIL="$1"
			shift
			;;
	esac
done

if [[ -n "$CSV_PATH" && -n "$USER_EMAIL" ]]; then
	echo "Error: --csv cannot be combined with an email argument."
	exit 1
fi

if [[ -z "$CSV_PATH" && -z "$USER_EMAIL" ]]; then
	echo "Usage: $0 [--admin] [--name <display_name>] <user_email>"
	echo "       $0 [--admin] --csv <path_to_csv>"
	exit 1
fi

CTFD_CONTAINER=$(check_ctfd_running)
echo "Found CTFd container '$CTFD_CONTAINER'"

if [[ -n "$CSV_PATH" ]]; then
	if [[ ! -f "$CSV_PATH" ]]; then
		echo "Error: CSV file not found: $CSV_PATH"
		exit 1
	fi

	CSV_FILENAME=$(basename "$CSV_PATH")
	HOST_INPUT_DIR=$(realpath "$(dirname "$BASH_SOURCE")/../input")

	if [[ "$(realpath "$CSV_PATH")" != "$HOST_INPUT_DIR"/* ]]; then
		echo "Copying $CSV_FILENAME into input/ directory..."
		cp "$CSV_PATH" "$HOST_INPUT_DIR/$CSV_FILENAME"
	fi

	USER_TYPE=$([[ -n "$ADMIN_FLAG" ]] && echo "admin users" || echo "users")
	prompt_user "Are you sure you want to create $USER_TYPE from $CSV_FILENAME?" && {
    ctfd_exec $CTFD_CONTAINER "PYTHONPATH=/opt/CTFd/ SCRIPT=true /opt/CTFd/CTFd/plugins/ng/scripts/create_user.py --csv $(printf '%q' "/opt/CTFd/input/$CSV_FILENAME") $ADMIN_FLAG"
  }
else
	echo -n "Enter password for $USER_EMAIL: "
	read -s USER_PASSWORD
	echo  # Add newline after hidden input

	if [[ -z "${USER_PASSWORD:-}" ]]; then
		echo "Error: Password cannot be empty"
		exit 1
	fi

	USER_TYPE=$([[ -n "$ADMIN_FLAG" ]] && echo "admin user" || echo "user")
	prompt_user "Are you sure you want to create a new $USER_TYPE ($USER_EMAIL)?" && {
    PYTHON_CMD="PYTHONPATH=/opt/CTFd/ SCRIPT=true /opt/CTFd/CTFd/plugins/ng/scripts/create_user.py $(printf '%q' "$USER_EMAIL") $(printf '%q' "$USER_PASSWORD") $ADMIN_FLAG"

    if [[ -n "$USER_NAME" ]]; then
      PYTHON_CMD="$PYTHON_CMD --name $(printf '%q' "$USER_NAME")"
    fi

    ctfd_exec $CTFD_CONTAINER "$PYTHON_CMD"
  }
fi
