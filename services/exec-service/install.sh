#!/bin/bash


echo "Setting up install"
mkdir -p /opt/service
cp -r .  /opt/service/

echo "Setting up systemd service"
cp ExecApp.service /usr/lib/systemd/system/

systemctl daemon-reload

echo "Running install"

echo "    installing nvm"
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash

cd /opt/service/

echo "    installing pnpm packages"
pnpm install

echo "Enabling systemd service"
systemctl enable ExecApp
systemctl start ExecApp
