#!/bin/sh
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

# print_step 0 "Checking /datadrive/prometheus directory"

# if [ ! -d "/datadrive/prometheus" ]; then
#     echo "   /datadrive/prometheus does not exist. Creating the directory structure."
    
#     # Check if /datadrive exists; if not, create it
#     if [ ! -d "/datadrive" ]; then
#         mkdir -p /datadrive
#         echo "   Created /datadrive directory."
#     fi
    
#     # Create /datadrive/prometheus
#     mkdir -p /datadrive/prometheus
#     echo "   Created /datadrive/prometheus directory."
# else
#     echo "   /datadrive/prometheus directory already exists."
# fi
# echo

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
        safe_exit 1
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

print_step 3 "Updating configs in monitor_config.yaml"

CONFIG_FILE="$AIOPSLAB_ROOT/aiopslab/observer/monitor_config.yaml"
CERT_PATH="$AIOPSLAB_ROOT/aiopslab/observer/ca.pem"
API_URL="http://localhost:9200"
PROMETHEUS_API_URL="http://localhost:32000"

# Detect OS and set correct sed syntax
case "$(uname -s)" in
    Darwin) SED_CMD="sed -i ''" ;;  # macOS
    Linux) SED_CMD="sed -i" ;;  # Linux
    *) echo "Unsupported OS"; exit 1 ;;
esac

# Ensure the configuration file exists
if [ -f "$CONFIG_FILE" ]; then
    echo "   Found monitor_config.yaml at $CONFIG_FILE."

    # Update es_cert_path
    $SED_CMD "s|^es_cert_path:.*|es_cert_path: '$CERT_PATH'|" "$CONFIG_FILE"
    echo "   Updated es_cert_path to $CERT_PATH."

    # Update API URL
    $SED_CMD "s|^api:.*|api: '$API_URL'|" "$CONFIG_FILE"
    echo "   Updated api to $API_URL."

    # Update Prometheus API URL
    $SED_CMD "s|^prometheusApi:.*|prometheusApi: '$PROMETHEUS_API_URL'|" "$CONFIG_FILE"
    echo "   Updated prometheusApi to $PROMETHEUS_API_URL."

    echo "   Verifying changes..."
    if grep -q "es_cert_path: *['\"]\?$CERT_PATH['\"]\?" "$CONFIG_FILE" && \
       grep -q "api: *['\"]\?$API_URL['\"]\?" "$CONFIG_FILE" && \
       grep -q "prometheusApi: *['\"]\?$PROMETHEUS_API_URL['\"]\?" "$CONFIG_FILE"; then
        echo "   All values updated successfully!"
    else
        echo "${RED}   Some values were not updated correctly. Please check $CONFIG_FILE manually.${NC}"
        exit 1
fi
else
    echo "${RED}   Configuration file $CONFIG_FILE not found. Ensure the AIOPSLAB_ROOT environment variable is set correctly.${NC}"
    exit 1
fi

echo