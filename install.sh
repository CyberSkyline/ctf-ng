#!/bin/bash

set -o pipefail
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_DIR="$SCRIPT_DIR/backend/"

prompt_user() {
  local message="$1"
  read -p "$message (y/n): " response
  if [[ "$response" == "y" || "$response" == "Y" ]]; then
    return 0
  else
    return 1
  fi
}

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
    corepack enable yarn
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
yarn install
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
  echo "Creating virtual environment in $PROJECT_DIR/venv..."
  python3 -m venv venv
fi

# Install deps
source "$PYTHON_DIR"venv/bin/activate
pip install --upgrade pip
pip install -r "$SCRIPT_DIR/external/CTFd/requirements.txt" # Install CTFd requirements
pip install -r "$PYTHON_DIR"ctfd/plugin/requirements.txt # Install our additional requirements

# Install ruff
curl -LsSf https://astral.sh/ruff/install.sh | sh

# Install pytest
if ! command -v pytest &> /dev/null; then
  prompt_user "Would you like to install pytest?" && {
    pip install -U pytest
  } || {
    echo "pytest installation aborted. Exiting."
    exit 1
  }
fi

echo "Installation completed successfully. Please restart your terminal session before attempting to start the server."
