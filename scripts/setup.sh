#!/bin/sh
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.


# Exit on any error
set -e

# Source utility functions
. "$(dirname "$0")/utils.sh"

# Trap for cleanup on script exit
trap cleanup INT TERM

# Check if node name is provided
if [ $# -eq 0 ]; then
    echo "${RED}Please provide the node on which prometheus will be deployed as an argument.${NC}"
    
    echo "Usage: $0 <node_name>"
    echo "    1. node_name should not be the cluster's control plane node."
    echo "    2. \`/datadrive/prometheus\` should exist on node with the write permissions."
    exit 1
fi

NODE_NAME="$1"

echo "${BOLD}Setting up required components for AIOpsLab...${NC}"
echo

# Step 1: Check prerequisites
. "$(dirname "$0")/steps/prereq.sh"

# Step 2: Create namespace
. "$(dirname "$0")/steps/ns.sh"

# Step 3: Deploy Prometheus
. "$(dirname "$0")/steps/deploy_prometheus.sh"

# Step 4: Build wrk2
. "$(dirname "$0")/steps/build_wrk.sh"

# Display final status
echo
display_final_status

echo
echo "${GREEN}${BOLD}Setup completed successfully.${NC}"