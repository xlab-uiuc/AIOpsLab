# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""Interface to run shell commands in the service cluster."""

import subprocess
import paramiko
import os
from aiopslab.paths import config


class Shell:
    """Interface to run shell commands in the service cluster.

    Note: this can only run a single command and get its output.
    TODO: expand to a stateful shell session interface.
    """
    def __init__(self, session = None):
        """Initialize the Shell class."""
        self._session = session
        
        # Configured via config.yml
        self._host = config.get("k8s_host", "localhost")
        self._user = config.get("k8s_user")
        self._ssh_key_path = config.get("ssh_key_path", "~/.ssh/id_rsa")

    def exec(self, command: str, input_data=None, cwd=None):
        """Execute a shell command on localhost, via SSH, or inside kind's control-plane container."""

        if self._host == "kind":
            return self.docker_exec("kind-control-plane", command)

        elif self._host == "localhost":
            print(
                "[WARNING] Running commands on localhost is not recommended. "
                "This may pose safety and security risks when using an AI agent locally. "
                "I hope you know what you're doing!!!"
            )
            return self.local_exec(command, input_data, cwd)

        else:
            return self.ssh_exec(self._host, self._user, self._ssh_key_path, command)

    def local_exec(self, command: str, input_data=None, cwd=None):
        if input_data is not None:
            input_data = input_data.encode("utf-8")

        try:
            out = subprocess.run(
                command,
                input=input_data,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
                cwd=cwd,
            )

            if out.stderr or out.returncode != 0:
                error_message = out.stderr.decode("utf-8")
                print(f"[ERROR] Command execution failed: {error_message}")
                return error_message
            else:
                output_message = out.stdout.decode("utf-8")
                print(output_message)
                return output_message

        except Exception as e:
            raise RuntimeError(f"Failed to execute command: {command}\nError: {str(e)}")

    def ssh_exec(self, host: str, user: str, ssh_key_path: str, command: str):
        ssh_key_path = os.path.expanduser(ssh_key_path)
        ssh_client = paramiko.SSHClient()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            ssh_client.connect(hostname=host, username=user, key_filename=ssh_key_path)

            stdin, stdout, stderr = ssh_client.exec_command(command)
            exit_status = stdout.channel.recv_exit_status()

            if exit_status != 0:
                error_message = stderr.read().decode("utf-8")
                return error_message
            else:
                output_message = stdout.read().decode("utf-8")
                print(output_message)
                return output_message

        except Exception as e:
            raise RuntimeError(f"Failed to execute command via SSH: {command}\nError: {str(e)}")

        finally:
            ssh_client.close()

    def docker_exec(self, container_name: str, command: str):
        """Execute a command inside a running Docker container."""
        escaped_command = command.replace('"', '\\"')
        
        docker_command = f'docker exec {container_name} sh -c "{escaped_command}"'

        try:
            out = subprocess.run(
                docker_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True
            )

            if out.stderr or out.returncode != 0:
                error_message = out.stderr.decode("utf-8")
                print(f"[ERROR] Docker command execution failed: {error_message}")
                return error_message
            else:
                output_message = out.stdout.decode("utf-8")
                print(output_message)
                return output_message

        except Exception as e:
            raise RuntimeError(f"Failed to execute command in Docker container: {container_name}\nError: {str(e)}")