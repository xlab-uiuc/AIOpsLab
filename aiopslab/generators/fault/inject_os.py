# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""Inject faults at the OS layer."""

import json
import yaml

from aiopslab.service.kubectl import KubeCtl
from aiopslab.generators.fault.base import FaultInjector


class OSFaultInjector(FaultInjector):
    def _inject(self, microservices: list[str], fault_type: str):
        if fault_type == "code":
            self.kernel_bug(microservices)
        else:
            print(f"Unknown fault type for OS level: {fault_type}")

    ############# FAULT LIBRARY ################

    # O.1: Kernel issue via the BPF filter
    def kernel_bug(self):
        return NotImplementedError

    ############# HELPER FUNCTIONS ################
