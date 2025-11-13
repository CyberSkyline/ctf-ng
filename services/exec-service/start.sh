#!/bin/bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

cd /opt/service/

echo "setting up node env"
nvm install 24

nvm run 24 "server.ts"
