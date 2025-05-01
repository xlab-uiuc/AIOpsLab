#!/bin/bash

export KUBECONFIG=$HOME/.kube/config
export TASK_NAME=$1
echo Running on $TASK_NAME
# kubectl delete ns openebs --force
# kubectl delete ns observe --force
# kubectl delete ns chaos-mesh --force
# kubectl delete ns test-hotel-reservation --force
# kubectl delete ns test-social-network --force
# kubectl delete ns astronomy-shop --force
# kubectl delete ns $(kubectl get ns --no-headers | awk '!/^(kube-flannel|kube-system|kube-public|kube-node-lease|default)/ {print $1}') --force
# kubectl delete pv --all --all-namespaces
# kubectl delete storageclass --all --all-namespaces
# kubectl delete crd --all --all-namespaces
# kubectl delete ns $(kubectl get ns --no-headers | awk '!/^(kube-flannel|kube-system|kube-public|kube-node-lease|default)/ {print $1}') --force
# kubectl delete pv --all --all-namespaces
# kubectl delete storageclass --all
# kubectl delete crd --all --all-namespaces
# kubectl delete pvc --all --all-namespaces
# sleep 120
timeout --foreground 30m python3 ./clients/gpt-full.py
exit_code=$?

if [ $exit_code -eq 124 ]; then
	echo "Task timeout."
elif [ $exit_code -eq 0 ]; then
	echo "Task success"
else
	echo "Task failed with: $exit_code"
fi
