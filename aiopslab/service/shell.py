# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""Interface to run shell commands in the service cluster."""

import subprocess


class Shell:
    """Interface to run shell commands in the service cluster.

    Note: this can only run a single command and get its output.
    TODO: expand to a stateful shell session interface.
    """

    @staticmethod
    def exec(command: str, input_data=None, cwd=None):
        """Execute a shell command with optional input data and return its output."""
        if input_data is not None:
            input_data = input_data.encode("utf-8")

        out = subprocess.run(
            command,
            input=input_data,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True,
            cwd=cwd,
        )

        if out.stderr or out.returncode != 0:
            return out.stderr.decode("utf-8")
        else:
            return out.stdout.decode("utf-8")
