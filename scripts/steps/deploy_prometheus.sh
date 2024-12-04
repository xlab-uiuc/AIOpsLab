#!/bin/sh

print_step 4 "Deploying 'Prometheus' service"

cleanup_pv_pvc() {
    echo "   Cleaning up existing PV and PVC..."
    kubectl delete pvc --all -n observe > /dev/null 2>&1 || true
    kubectl delete pv prometheus-pv > /dev/null 2>&1 || true
}

update_node_affinity() {
    sed -i "s/- kubecontroller/- $NODE_NAME/" "$PROMETHEUS_PV_FILE"
    echo "   Updated node affinity to: $NODE_NAME"
}

# Check if Prometheus is already deployed and running
if helm list -n observe 2>/dev/null | grep -q "prometheus" && is_prometheus_running; then
    print_result 0
    echo "   Prometheus is already deployed and running."
else
    # Clean up existing PV and PVC
    cleanup_pv_pvc

    # Update node affinity in PV file
    update_node_affinity

    # Apply Prometheus PersistentVolume
    if kubectl apply -f "$PROMETHEUS_PV_FILE" > /dev/null; then
        echo "   Applied Prometheus PersistentVolume."
    else
        print_result 1
        echo "${RED}   Failed to apply Prometheus PersistentVolume.${NC}"
        exit 1
    fi

    # Uninstall existing Prometheus installation if it exists
    if helm list -n observe 2>/dev/null | grep -q "prometheus"; then
        echo "   Uninstalling existing Prometheus installation..."
        helm uninstall prometheus -n observe
    fi

    # Install Prometheus using Helm
    if helm install prometheus "$PROMETHEUS_CHART_PATH" -n observe --set server.persistentVolume.storageClass=local-storage > /dev/null 2>&1; then
        echo "   Prometheus deployment started."
    else
        print_result 1
        echo "${RED}   Failed to start Prometheus deployment.${NC}"
        exit 1
    fi

    # Wait for Prometheus pods to be running
    echo "   Waiting for Prometheus pods to be running ..."
    max_attempts=5
    attempt=1
    while [ $attempt -le $max_attempts ]; do
        if is_prometheus_running; then
            printf "   Prometheus is now running."
            print_result 0
            break
        fi
        echo "   Attempt $attempt/$max_attempts: Prometheus is not yet ready. Waiting 10s ..."
        sleep 10
        attempt=$((attempt + 1))
    done

    if [ $attempt -gt $max_attempts ]; then
        print_result 1
        echo "${RED}   Prometheus did not become ready within the expected time.${NC}"
        echo "   Checking pod status:"
        kubectl get pods -n observe -l app.kubernetes.io/name=prometheus
        echo "\n   Checking events for Prometheus pods:"
        kubectl get events -n observe --sort-by=.metadata.creationTimestamp | grep prometheus
        echo "\n   Checking Persistent Volume status:"
        kubectl get pv
        echo "\n   Checking Persistent Volume Claim status:"
        kubectl get pvc -n observe
        echo "\n   Checking node affinity of PV:"
        kubectl get pv prometheus-pv -o yaml | grep -A 5 nodeAffinity
        echo "\n   Checking available nodes:"
        kubectl get nodes
        exit 1
    fi
fi
echo