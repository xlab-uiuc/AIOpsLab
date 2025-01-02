#!/bin/sh

# Determine the script directory 
if [ -n "${BASH_SOURCE[0]}" ]; then
    # Bash shell
    SCRIPT_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
elif [ -n "$ZSH_VERSION" ]; then
    # Zsh shell
    SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
else
    # POSIX sh fallback
    SCRIPT_DIR=$(cd "$(dirname "$_")" && pwd)
fi


# Source the utils.sh file
. "$SCRIPT_DIR/utils.sh"

if is_sourced; then
    echo "DEBUG: Script is being sourced."
    set +e
else
    echo "DEBUG: Script is being executed."
    set -e
    trap 'cleanup' INT TERM
fi


# Trap for cleanup on script exit
# trap 'safe_exit 1' INT TERM

# Simulate an error
# if [ ! -d "/nonexistent/path" ]; then
#     echo "Error: Directory does not exist."
#     safe_exit 1
# fi

# Check if node name is provided
if [ $# -eq 0 ]; then
    echo "${RED}Please provide the node on which prometheus will be deployed as an argument.${NC}"
    
    echo "Usage: $0 <node_name> [custom_prometheus_path]"
    echo "    1. node_name should be the one of the cluster's nodes."
    # should not be the cluster's control plane node."
    echo "    2. [custom_prometheus_path] should exist on the specified node with write permissions. Otherwise, it will use \`/datadrive/prometheus\`."
    safe_exit 1
fi

NODE_NAME="$1"
CUSTOM_PROMETHEUS_PATH="${2:-/datadrive/prometheus}" # Default to /datadrive/prometheus if not provided

printf "${BOLD}Setting up required components for AIOpsLab...${NC}\n"
echo


# Step 1: Check prerequisites
. "$SCRIPT_DIR/steps/prereq.sh"

# Step 2: Create namespace
. "$SCRIPT_DIR/steps/ns.sh"

# Step 3: Deploy Prometheus
. "$SCRIPT_DIR/steps/deploy_prometheus.sh"

# Step 4: Build wrk2
. "$SCRIPT_DIR/steps/build_wrk.sh"

# Display final status
printf "\n"
display_final_status

printf "\n"
printf "${GREEN}${BOLD}Setup completed successfully.${NC}\n"