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

# Prompt the user for their GitHub token
echo "Please provide your GitHub personal access token with permissions to write SSH keys."
echo "If you don't have a token or don't want to provide it, press Enter, and you will be prompted to manually add the public key to GitHub."

read -p "GitHub Access Token (leave blank if not providing): " github_token

# Check if the token was provided
if [ -z "$github_token" ]; then
    # Token not provided, ask user to add the key manually
    ssh_pub_key=$(cat ~/.ssh/id_rsa.pub)
    echo "No token provided. Please copy the following SSH public key to your GitHub account manually:"
    echo
    echo "$ssh_pub_key"
    echo
    echo "To add the SSH key to your GitHub account manually, go to:"
    echo "https://github.com/settings/keys"
    echo "Click on 'New SSH Key' and paste the key."
    read -p "Press Enter after you have added the key to continue."
    echo "Sleeping for 30 seconds"
    sleep 30
else
    # Token provided, try to add the SSH key using the GitHub API
    add_ssh_key_to_github "$github_token"
    sleep 5
fi

# AIOpsLab setup
GIT_SSH_COMMAND="ssh -o StrictHostKeyChecking=accept-new" git clone --recurse-submodules git@github.com:marvin233/AIOpsLab.git
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


