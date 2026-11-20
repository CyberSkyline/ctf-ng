#!/bin/bash

# Runs every suite CI runs: testrunner.yml (backend) and chall-check-testrunner.yml (parser, chall-check).
# Each suite runs even if an earlier one fails; the exit code is non-zero if any failed.

set -uo pipefail

ROOT=$(realpath "$(dirname $BASH_SOURCE)/..")
PYTHON="$ROOT/backend/venv/bin/python"
status=0

pnpm --filter backend test || status=1

# The backend venv has the published parser and chall-check installed; put the repo's source first
# so these suites test the code in this checkout, like CI's editable installs do
export PYTHONPATH="$ROOT/lib/parser/src:$ROOT/tools/chall-check/src"

(cd "$ROOT/tools/chall-check" && "$PYTHON" -m pytest) || status=1
(cd "$ROOT/lib/parser" && "$PYTHON" -m pytest) || status=1

exit $status
