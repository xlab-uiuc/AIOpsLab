#!/bin/sh

# List of namespaces to create
namespaces="observe test-social-network test-hotel-reservation"


print_step 3 "Setting up namespaces for AIOpsLab"
echo

# Loop through each namespace
for namespace in $namespaces; do

    # Check if namespace already exists
    if kubectl get namespace "$namespace" > /dev/null 2>&1; then
        printf "   Namespace '$namespace' already exists."
        print_result 0
    # Create if it doesn't exist
    else
        if kubectl create namespace "$namespace" > /dev/null; then
            printf "   Namespace '$namespace' created successfully."
            print_result 0
        else
            printf "${RED}   Failed to create '$namespace' namespace.${NC}"
            print_result 1
            safe_exit 1
        fi
    fi

    # Verify the namespace exists and is active
    namespace_status=$(kubectl get namespace "$namespace" -o jsonpath='{.status.phase}' 2>/dev/null)
    if [ "$namespace_status" = "Active" ]; then
        echo "   '$namespace' namespace is active and ready."
    else
        printf "${RED}   '$namespace' namespace is not active or doesn't exist.${NC}"
        print_result 1
        echo "   Current namespaces:"
        kubectl get namespaces
        safe_exit 1
    fi
    echo
done