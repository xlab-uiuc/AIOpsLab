# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

import os
import subprocess
import threading
import time
from aiopslab.service.helm import Helm
from aiopslab.service.kubectl import KubeCtl
from aiopslab.generators.fault.base import FaultInjector

class SymptomFaultInjector(FaultInjector):
    def __init__(self, namespace: str):
        super().__init__(namespace)
        self.namespace = namespace
        self.kubectl = KubeCtl()
        self.kubectl.create_namespace_if_not_exist("chaos-mesh")
        Helm.add_repo("chaos-mesh", "https://charts.chaos-mesh.org")
        chaos_configs = {
            "release_name": "chaos-mesh",
            "chart_path": "chaos-mesh/chaos-mesh",
            "namespace": "chaos-mesh",
            "version": "2.6.2",
        }
        Helm.install(**chaos_configs)
        time.sleep(6)
        # Helm.uninstall(**sn_configs)
        
    def recover_pod_failure(self):
        """
        Recover a pod failure fault. Shortcut to directly kubectl delete the yaml.
        """
        chaos_yaml_path = f"/tmp/pod-failure-experiment.yaml"
        command = f"kubectl delete -f {chaos_yaml_path}"
        result = self.kubectl.exec_command(command)
        print(f"Cleaned up chaos experiment: {result}")

    def inject_pod_failure(self, microservices, duration: str = "30s"):
        """
        Inject a pod failure fault.
        """
        chaos_experiment = {
            "apiVersion": "chaos-mesh.org/v1alpha1",
            "kind": "PodChaos",
            "metadata": {
                "name": "pod-failure-experiment",
                "namespace": self.namespace
            },
            "spec": {
                "action": "pod-failure",
                "mode": "one",
                "duration": duration,
                "selector": {
                    "labelSelectors": {
                        'io.kompose.service': ", ".join(microservices)
                    } 
                }
            }
        }

        chaos_yaml_path = f"/tmp/pod-failure-experiment.yaml"
        with open(chaos_yaml_path, "w") as yaml_file:
            import yaml
            yaml.dump(chaos_experiment, yaml_file)

        command = f"kubectl apply -f {chaos_yaml_path}"
        result = self.kubectl.exec_command(command)
        print(f"Applied chaos experiment: {result}")

    def recover_network_loss(self):
        chaos_yaml_path = f"/tmp/network-loss-experiment.yaml"
        command = f"kubectl delete -f {chaos_yaml_path}"
        result = self.kubectl.exec_command(command)
        print(f"Cleaned up chaos experiment: {result}")

    def inject_network_loss(self, microservices, duration: str = "30s"):
        """
        Inject a network loss fault.
        """
        chaos_experiment = {
            "apiVersion": "chaos-mesh.org/v1alpha1",
            "kind": "NetworkChaos",
            "metadata": {
                "name": "loss",
                "namespace": self.namespace
            },
            "spec": {
                "action": "loss",
                "mode": "one",
                "duration": duration,
                "selector": {
                    "namespaces": [self.namespace],
                    "labelSelectors": {
                        'io.kompose.service': ", ".join(microservices)
                    }
                },
                "loss": {
                    "loss": "99",
                    "correlation": "100"
                }
            }
        }

        chaos_yaml_path = f"/tmp/network-loss-experiment.yaml"
        with open(chaos_yaml_path, "w") as yaml_file:
            import yaml
            yaml.dump(chaos_experiment, yaml_file)

        command = f"kubectl apply -f {chaos_yaml_path}"
        result = self.kubectl.exec_command(command)
        print(f"Applied network loss experiment: {result}")
    
    # def inject_network_delay(self):
    #     pass
        
    # def _inject_pod_kill(self):
    #     pass

    # def _inject_container_kill(self):
    #     pass


if __name__ == "__main__":
    namespace = "test-hotel-reservation"
    microservices = ["geo"]
    fault_type = "pod_failure"
    injector = SymptomFaultInjector(namespace)
    injector._inject(fault_type, microservices, '30s')
    injector._recover(fault_type)

