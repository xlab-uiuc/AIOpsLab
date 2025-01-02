#!/bin/sh
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.


# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color
BOLD='\033[0;36m'  #'\033[1m'

# ASCII Symbols
CHECK_MARK="[OK]"
CROSS_MARK="[FAILED]"

# PATHS
# SCRIPT_DIR=$(dirname "$0")
AIOPSLAB_ROOT=$(cd "$SCRIPT_DIR/.." && pwd)
PROMETHEUS_PV_FILE="$AIOPSLAB_ROOT/aiopslab/observer/prometheus/prometheus-pv.yml"
PROMETHEUS_CHART_PATH="$AIOPSLAB_ROOT/aiopslab/observer/prometheus/prometheus"

print_step() {
    printf "${BOLD}Setup %d:${NC} %s" "$1" "$2"
}

# # Check if the script is sourced (POSIX-compatible)
# is_sourced() {
#     [ "$0" != "$(basename -- "$0")" ]
# }

# Check if the script is sourced
is_sourced() {
    [ "${BASH_SOURCE[0]}" != "$0" ] 2>/dev/null || [ "$_" != "$0" ]
}

safe_exit() {
    if is_sourced; then
        return "$1" 2>/dev/null || true
    else
        exit "$1" # Exit with the same exit code
    fi
}

print_result() {
    if [ $1 -eq 0 ]; then
        printf " ${GREEN}${CHECK_MARK}${NC}\n"
    else
        printf " ${RED}${CROSS_MARK}${NC}\n"
    fi
}

command_exists() {
    command -v "$1" >/dev/null 2>&1
}

is_prometheus_running() {
    kubectl get pods -n observe -l app.kubernetes.io/name=prometheus | grep -q Running
}

cleanup() {
    echo "\nCleaning up..."
    pkill -P $$ || true
    safe_exit 1
}

display_final_status() {
    printf "${BOLD}Final Status:${NC}\n"
    namespace_info=$(kubectl get namespaces -o=custom-columns=NAME:.metadata.name,STATUS:.status.phase,AGE:.metadata.creationTimestamp --no-headers)
    printf "   %-30s %-10s %-20s\n" "NAME" "STATUS" "AGE"
    echo "$namespace_info" | while read -r name status age; do
        age_seconds=$(($(date +%s) - $(date -d "$age" +%s)))
        if [ $age_seconds -lt 60 ]; then
            age_display="${age_seconds}s"
        elif [ $age_seconds -lt 3600 ]; then
            age_display="$((age_seconds / 60))m"
        elif [ $age_seconds -lt 86400 ]; then
            age_display="$((age_seconds / 3600))h$((age_seconds % 3600 / 60))m"
        else
            age_display="$((age_seconds / 86400))d$((age_seconds % 86400 / 3600))h"
        fi
        printf "   %-30s %-10s %-20s\n" "$name" "$status" "$age_display"
    done
}
