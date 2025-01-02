# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""Interface to the wrk workload generator."""

import subprocess
import re


class Wrk:
    def __init__(
        self, rate, dist="norm", connections=2, duration=6, threads=2, latency=True
    ):
        """Interface to the wrk workload generator.

        Args:
            rate (int): The work rate (throughput) in requests/sec (total). Defaults to None.
            dist (str, optional): The distribution of requests [fixed, exp, norm, zipf]. Defaults to "norm".
            connections (int, optional): The number of connections to keep open. Defaults to 2.
            duration (str, optional): The duration of the test. Defaults to 10 sec.
            threads (int, optional): The number of threads to use. Defaults to 2.
            latency (bool, optional): Whether to measure latency. Defaults to False.
        """
        self.rate = rate
        self.dist = dist
        self.connections = connections
        self.duration = duration
        self.threads = threads
        self.latency = latency

    def start_workload(self, payload_script: str, url: str):
        """Start the wrk workload.

        Args:
            payload_script (str): The path to the wrk payload Lua script.
            url (str): The URL of the target server.
        """

        command = f"wrk -D {self.dist} -t {self.threads} -c {self.connections} -d {self.duration} -L -s {payload_script} {url} -R {self.rate}"
        command += " --latency" if self.latency else ""
        process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
        output, error = process.communicate()

        if error:
            print(error.decode("utf-8"))
        else:
            print(output.decode("utf-8"))
            stats = self._parse_output(output.decode("utf-8"))
            print(stats)

    def _parse_output(self, text):
        """Helper function to parse the output of the wrk tool."""
        patterns = {
            "average_latency_ms": r"Mean\s+=\s+([\d.]+),",
            "stddev_latency_ms": r"StdDeviation\s+=\s+([\d.]+)",
            "max_latency_ms": r"Max\s+=\s+([\d.]+),",
            "total_count": r"Total count\s+=\s+(\d+)",
            "requests_per_second": r"Requests/sec:\s+([\d.]+)",
            "transfer_per_second_KB": r"Transfer/sec:\s+([\d.]+)KB",
            "non_2xx_3xx_responses": r"Non-2xx or 3xx responses:\s+(\d+)",
        }

        parsed_data = {}
        for key, pattern in patterns.items():
            match = re.search(pattern, text)
            if match:
                parsed_data[key] = (
                    float(match.group(1))
                    if "ms" in key or "second" in key
                    else int(match.group(1))
                )

        histogram_pattern = r"(\d+\.\d+)%\s+([\d.]+)(\w+)"
        histogram_matches = re.findall(histogram_pattern, text, re.MULTILINE)
        histogram_data = {
            float(percentile): float(value)
            for percentile, value, _ in histogram_matches
        }
        unit = histogram_matches[0][2]
        parsed_data[f"histogram_data_{unit}"] = histogram_data

        return parsed_data
