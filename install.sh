#!/bin/bash

prompt_user() {
  local message="$1"
  read -p "$message (y/n): " response
  if [[ "$response" == "y" || "$response" == "Y" ]]; then
    return 0
  else
    return 1
  fi
}

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

echo "Installation completed successfully. Please restart your terminal session before attempting to start the server."