#!/bin/bash

# Function to generate an SSH key if not already present
generate_ssh_key() {
    if [ ! -f ~/.ssh/id_rsa ]; then
        echo "SSH key not found. Generating one..."
        ssh-keygen -t rsa -N "" -f ~/.ssh/id_rsa
        echo "SSH key generated."
    else
        echo "SSH key already exists."
    fi
}

# Function to add SSH key to GitHub using API and access token
add_ssh_key_to_github() {
    ssh_pub_key=$(cat ~/.ssh/id_rsa.pub)
    key_title="VM SSH Key $(date +%Y-%m-%d)"

    response=$(curl -s -H "Authorization: token $1" \
        -H "Accept: application/vnd.github.v3+json" \
        https://api.github.com/user/keys \
        -d "{\"title\":\"$key_title\",\"key\":\"$ssh_pub_key\"}")

    if echo "$response" | grep -q "key"; then
        echo "SSH key successfully added to GitHub."
    else
        echo "Failed to add SSH key to GitHub. Please check your token and permissions."
        echo "Response: $response"
    fi
}

# Generate the SSH key if it's not already there
generate_ssh_key

# AIOpsLab setup
GIT_SSH_COMMAND="ssh -o StrictHostKeyChecking=accept-new" git clone git@github.com:microsoft/AIOpsLab.git
cd AIOpsLab
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install -y python3.11
sudo apt-get install -y python3.11-venv
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
.venv/bin/pip install -U pip setuptools
.venv/bin/pip install poetry
.venv/bin/poetry install

# DeathStarBench prerequisites
sudo apt install -yq python3-pip datamash libssl-dev libz-dev luarocks python3-pip unzip
pip3 install -q crossplane pandas PyYAML numpy kubernetes scikit-optimize aiohttp
sudo luarocks install luasocket


# Install Helm
sudo snap install helm --classic


