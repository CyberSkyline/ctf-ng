#!/bin/bash

set -euo pipefail

if [ "$EUID" -eq 0 ]; then
  echo "This script must not be run as root. Please run as a non-root user."
  exit 1
fi

source .scripts/utils.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_DIR="$SCRIPT_DIR/backend/"

sudo apt-get update

# Configure submodules
git submodule update --init --recursive # Initialize submodules
git config --local submodule.recurse true # Configures git to automatically update submodules when pulling or switching branches

# Add CTFd to the pythonpath via .env file
PYTHONPATH_LINE="PYTHONPATH=$(pwd)/external/CTFd"
if [ ! -f ".env" ]; then
  echo "$PYTHONPATH_LINE" > ".env"
elif ! grep -Fxq "PYTHONPATH" ".env"; then
  echo "$PYTHONPATH_LINE" >> ".env"
fi

# Set up default .env.dev and .env.prod files if they do not exist
if [ ! -f ".env.dev" ]; then
  cp ./conf/ctfd/.env.default.dev .env.dev
fi

if [ ! -f ".env.prod" ]; then
  cp ./conf/ctfd/.env.default.prod .env.prod
fi

if [ ! -f ".env.staging" ]; then
  cp ./conf/ctfd/.env.default.prod .env.staging
fi

# Add OAuth placeholders to .env files if not already present
for envfile in .env .env.dev .env.prod .env.staging; do
  if [ -f "$envfile" ]; then
    if ! grep -qi "OAuth" "$envfile"; then
      cat <<'EOF' >> "$envfile"

# OAuth
OKTA_CLIENT_ID = -
OKTA_CLIENT_SECRET = -
OKTA_DOMAIN = -
SERVER_DOMAIN = -
EOF
    fi
  fi
done

# Docker
if ! command -v docker &> /dev/null; then
  echo "Docker is not installed."
  
  prompt_user "Would you like to install Docker?" && {
    if [[ "$OSTYPE" == "linux-gnu"* && -f /etc/os-release && $(grep -i 'ubuntu' /etc/os-release) ]]; then
      echo "Installing Docker on Linux..."

      # Add GPG key
      sudo apt-get update
      sudo apt install apt-transport-https ca-certificates curl software-properties-common lsb-release gnupg -y
      curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
      
      # Add docker repository
      echo \
        "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] \
        https://download.docker.com/linux/ubuntu \
        $(lsb_release -cs) stable" | \
        sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

      # Install Docker
      sudo apt update
      sudo apt install docker-ce docker-ce-cli containerd.io -y
    else
      echo "Unsupported OS. Please install Docker manually."
      exit 1
    fi
  } || {
    echo "Docker installation aborted. Exiting."
    exit 1
  }
fi

# Configure non-root users to run Docker commands
if ! id -nG "$USER" | grep -qw "docker"; then
  echo "User $USER is not in the docker group."
  prompt_user "Would you like to allow non-root users to run Docker commands?" && {
    sudo groupadd docker
    sudo usermod -aG docker $USER
  } || {
    echo "Non-root user access to Docker commands not granted."
  }
fi

# Install npm / node
if ! command -v npm &> /dev/null; then
  prompt_user "Would you like to install node and npm?" && {
    curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
    \. "$HOME/.nvm/nvm.sh"
    nvm install 24
    corepack enable pnpm
  } || {
    echo "node + vite installation aborted. Exiting."
    exit 1
  }
fi

# Install vite
if ! command -v vite &> /dev/null; then
  prompt_user "Would you like to install vite?" && {
    npm install -g vite
  } || {
    echo "vite installation aborted. Exiting."
    exit 1
  }
fi

# Install vite deps
cd ./frontend
pnpm install
cd -

# Install pip
if ! command -v pip3 &> /dev/null; then
  prompt_user "Would you like to install pip?" && {
    sudo apt-get install python3-pip -y
  } || {
    echo "pip installation aborted. Exiting."
    exit 1
  }
fi

# Install python3-venv
sudo apt-get install python3-venv -y

# Install backend deps
cd "$PYTHON_DIR"

# Create virtual environment if not already present
if [ ! -d "venv" ]; then
  echo "Creating virtual environment in $PYTHON_DIR/venv..."
  python3 -m venv venv
fi

# Install deps
source "$PYTHON_DIR"venv/bin/activate
pip install --upgrade pip
pip install -r "$SCRIPT_DIR/external/CTFd/requirements.txt" # Install CTFd requirements
pip install -r "$PYTHON_DIR"ng/requirements.txt # Install our additional requirements
pip install cyber-skyline-chall-check
chall-check --install-completion

# Install ruff
if ! command -v ruff &> /dev/null; then
  prompt_user "Would you like to install ruff?" && {
    curl -LsSf https://astral.sh/ruff/install.sh | sh
  } || {
    echo "ruff installation aborted. Exiting."
    exit 1
  }
fi

# Install pytest
if ! command -v pytest &> /dev/null; then
  prompt_user "Would you like to install pytest?" && {
    pip install -U pytest
  } || {
    echo "pytest installation aborted. Exiting."
    exit 1
  }
fi

prompt_user "Would you like to generate tls certs for docker? You will be prompted" && {
  mkdir ssl
  cd ssl
  read -p "Please enter the ip of your dev instance" machineip
  openssl genrsa -aes256 -out ca-key.pem 4096
  openssl req -new -x509 -days 365 -key ca-key.pem -sha256 -out ca.pem
  openssl genrsa -out server-key.pem 4096
  openssl req -subj "/CN=$machineip" -sha256 -new -key server-key.pem -out server.csr
  echo subjectAltName = IP:$machineip,IP:127.0.0.1 >> extfile.cnf
  echo extendedKeyUsage = serverAuth >> extfile.cnf
  openssl x509 -req -days 365 -sha256 -in server.csr -CA ca.pem -CAkey ca-key.pem -CAcreateserial -out server-cert.pem -extfile extfile.cnf
  echo "Server keys generated moving to client keys"
  mkdir client
  cd client
  openssl genrsa -out key.pem 4096
  openssl req -subj '/CN=client' -new -key key.pem -out client.csr
  echo extendedKeyUsage = clientAuth > extfile-client.cnf
  openssl x509 -req -days 365 -sha256 -in client.csr -CA ../ca.pem -CAkey ../ca-key.pem -CAcreateserial -out cert.pem -extfile extfile-client.cnf

  echo "Certs generated"
  echo "Copying certs and configs"
  mkdir -p ~/.docker/
  cp ../ca.pem ~/.docker/
  cp cert.pem ~/.docker/
  cp key.pem ~/.docker/
  sudo mkdir -p /var/lib/certs/ssl/
  sudo cp ~/.docker/* /var/lib/certs/ssl/
  cd ../
  sudo mkdir -p /etc/docker/ssl
  sudo cp ca.pem /etc/docker/ssl
  sudo cp server-cert.pem /etc/docker/ssl
  sudo cp server-key.pem /etc/docker/ssl
  echo '{
    "tlsverify": true,
    "tlscacert": "/etc/docker/ssl/ca.pem",
    "tlscert": "/etc/docker/ssl/server-cert.pem",
    "tlskey": "/etc/docker/ssl/server-key.pem",
    "default-ulimit": "nofile=50:100",
    "hosts": ["unix:///var/run/docker.sock", "tcp://0.0.0.0:2376"]
  }' > daemon.json
  sudo cp daemon.json /etc/docker/
  rm daemon.json
  echo "Please restart your docker daemon. You may have to start it mannually from the cli calling dockerd"
  echo "Add the following to your zshrc/bashrc/fishrc make sure the homepath is reflective of your user"
  echo 'export DOCKER_HOST="127.0.0.1:2376"
export DOCKER_TLS_VERIFY="true"
export DOCKER_CERT_PATH=/home/ubuntu/.docker/'
  
} || {
  echo "TLS gen aborted"
  exit 1
}

echo "Installation completed successfully. Please restart your terminal session before attempting to start the server."
