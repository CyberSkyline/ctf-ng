#!/bin/bash

set -euo pipefail

cd /opt/CTFd/

install_plugin_deps() {
  ## Install plugins deps on load
  for d in /opt/CTFd/CTFd/plugins/*; do
    if [ -f "$d/requirements.txt" ]; then
      pip install --no-cache-dir -r "$d/requirements.txt";
    fi;
  done;
}

start_dev() {
  celery -A CTFd.plugins.ng.containers.tasks worker --loglevel=INFO &
  python serve_debug.py
}

start_prod() {
  WORKERS=${WORKERS:-1}
  WORKER_CLASS=${WORKER_CLASS:-geventwebsocket.gunicorn.workers.GeventWebSocketWorker}
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
    python ping.py
  fi

  # Initialize database
  flask db upgrade

  celery -A CTFd.plugins.ng.containers.tasks worker --loglevel=INFO &

  # Start CTFd
  echo "Starting CTFd"
  exec gunicorn 'CTFd:create_app()' \
      --bind '0.0.0.0:8000' \
      --workers $WORKERS \
      --worker-tmp-dir "$WORKER_TEMP_DIR" \
      --worker-class "$WORKER_CLASS" \
      --access-logfile "$ACCESS_LOG" \
      --error-logfile "$ERROR_LOG"
}

## MAIN ##
install_plugin_deps

if [ "${DEBUG:-}" == "false" ]; then
  start_prod
else
  start_dev
fi
