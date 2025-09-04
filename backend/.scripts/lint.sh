#!/bin/bash

set -euo pipefail

source venv/bin/activate

ruff check --config ./pyproject.toml
