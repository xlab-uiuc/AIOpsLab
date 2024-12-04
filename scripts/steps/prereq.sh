#!/bin/sh
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

print_step 0 "Checking /datadrive/prometheus directory"
if [ ! -d "/datadrive/prometheus" ]; then
    echo "   /datadrive/prometheus does not exist. Creating the directory structure."
    
    # Check if /datadrive exists; if not, create it
    if [ ! -d "/datadrive" ]; then
        sudo mkdir -p /datadrive
        echo "   Created /datadrive directory."
    fi
    
    # Create /datadrive/prometheus
    sudo mkdir -p /datadrive/prometheus
    echo "   Created /datadrive/prometheus directory."
else
    echo "   /datadrive/prometheus directory already exists."
fi
echo

print_step 1 "Checking kubectl installation"
if command_exists kubectl; then
    kubectl_path=$(which kubectl)
    print_result 0
    echo "   kubectl is available at: ${kubectl_path}"
else
    print_result 1
    echo "   kubectl is not found in the current PATH."
    echo "   Checking common installation locations..."
    
    for location in "/usr/local/bin/kubectl" "/usr/bin/kubectl" "$HOME/.local/bin/kubectl" "$HOME/bin/kubectl"; do
        if [ -x "$location" ]; then
            echo "   kubectl found at $location"
            export PATH="$PATH:$(dirname "$location")"
            kubectl_path=$location
            break
        fi
    done
    
    if ! command_exists kubectl; then
        echo "${RED}   kubectl is not installed or not in PATH. Please install kubectl before running AIOpsLab.${NC}"
        exit 1
    fi
fi
echo

print_step 2 "Checking Helm installation"
if command_exists helm; then
    helm_path=$(which helm)
    print_result 0
    echo "   Helm is available at: ${helm_path}"
else
    print_result 1
    echo "${RED}   Helm is not installed. Please install Helm before running AIOpsLab.${NC}"
    exit 1
fi
echo