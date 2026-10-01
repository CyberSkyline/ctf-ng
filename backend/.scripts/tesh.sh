#!/bin/bash

set -uo pipefail

source venv/bin/activate

cd ng/

# Mirror .github/workflows/testrunner.yml: the middleware suite runs even if the main suite fails
make test-all
main_status=$?

make test-middleware
middleware_status=$?

exit $(( main_status || middleware_status ))
