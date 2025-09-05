#!/bin/bash

set -euo pipefail

source venv/bin/activate

cd ng/
make test-all