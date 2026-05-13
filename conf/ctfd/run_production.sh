#!/bin/bash
set -euo pipefail

export APP_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

eval "$(python3 "$APP_ROOT/conf/ctfd/init_secrets.py")"

WORKERS=${WORKERS:-1}
WORKER_CLASS=${WORKER_CLASS:-gevent}
ACCESS_LOG=${ACCESS_LOG:--}
ERROR_LOG=${ERROR_LOG:--}
WORKER_TEMP_DIR=${WORKER_TEMP_DIR:-/dev/shm}
SECRET_KEY=${SECRET_KEY:-}
SKIP_DB_PING=${SKIP_DB_PING:-false}

# Check that a .ctfd_secret_key file or SECRET_KEY envvar is set
if [ ! -f .ctfd_secret_key ] && [ -z "$SECRET_KEY" ]; then
    if [ $WORKERS -gt 1 ]; then
        echo "[ ERROR ] You are configured to use more than 1 worker."
        echo "[ ERROR ] To do this, you must define the SECRET_KEY environment variable or create a .ctfd_secret_key file."
        echo "[ ERROR ] Exiting..."
        exit 1
    fi
fi

# Skip db ping if SKIP_DB_PING is set to a value other than false or empty string
if [[ "$SKIP_DB_PING" == "false" ]]; then
  # Ensures that the database is available
  python3 ping.py
fi

# Initialize database
flask db upgrade

celery -A CTFd.plugins.ng.containers.tasks worker --loglevel=INFO &

# Start CTFd (without exec so the shell stays as PID 1 and manages both processes)
echo "Starting CTFd"
gunicorn 'CTFd:create_app()' \
    --bind '0.0.0.0:8000' \
    --workers $WORKERS \
    --worker-tmp-dir "$WORKER_TEMP_DIR" \
    --worker-class "$WORKER_CLASS" \
    --access-logfile "$ACCESS_LOG" \
    --error-logfile "$ERROR_LOG"
