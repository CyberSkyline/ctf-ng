#!/bin/bash

set -euo pipefail

source venv/bin/activate

pip install --upgrade pip
pip install -r ../external/CTFd/requirements.txt # Install CTFd deps
pip install -r ng/requirements.txt # Install our additional requirements
pip install --upgrade cyber-skyline-chall-check
chall-check --install-completion
