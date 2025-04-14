# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""Define and query information about an AIOps Root Cause Analysis task."""

import textwrap
from typing import Any

from aiopslab.orchestrator.tasks.base import Task
from aiopslab.orchestrator.actions.analysis import AnalysisActions
from aiopslab.service.apps.base import Application
from aiopslab.session import SessionItem
from aiopslab.utils.actions import get_actions
from aiopslab.utils.status import InvalidActionError


class AnalysisTask(Task):
    """An AIOps root cause analysis task."""

    def __init__(self, app: Application):
        super().__init__()
        self.app = app
        self.helm_configs = self.app.helm_configs
        self.app_summary = self.app.get_app_summary()
        self.actions = AnalysisActions()

        self.task_desc = """\
            You are an expert DevOps engineer who has been tasked with doing root cause analysis in a deployed service.

            The service you are working with today is described below:
            {app_summary}

            You will begin by analyzing the service's state and telemetry, and then submit one of two possible solutions:
            1. dict[str, str]: A dictionary with two keys: 'system_level' and 'fault_type'.
                - system_level: The system level at which the fault occurred. Please choose from the following options:
                    - 'Hardware'
                    - 'Operating System'
                    - 'Virtualization'
                    - 'Application'
                - fault_type: The type of fault that occurred. Please choose from the following options:
                    - 'Misconfiguration'
                    - 'Code Defect'
                    - 'Authentication Issue'
                    - 'Network/Storage Issue'
                    - 'Operation Error'
                    - 'Dependency Problem'
            
            2. str: `None` if no faults were detected
            """

        self.instructions = """\
            You will respond with one of the above APIs as your next action.
            Please respond in the following format in a markdown code block:
            ```
            <API_NAME>(<API_PARAM1>, <API_PARAM2> ...)
            ```

            For example:
            ```
            exec_shell("ls -l")      # will list files in current directory
            ```

            Please respond with only a single action per turn.
            """

    def get_task_description(self):
        return textwrap.dedent(self.task_desc).format(app_summary=self.app_summary)

    def get_instructions(self):
        return textwrap.dedent(self.instructions)

    def get_available_actions(self):
        return get_actions(task="analysis")

    def perform_action(self, action_name, *args, **kwargs):
        action_method = getattr(self.actions, action_name, None)

        if action_method is not None and callable(action_method):
            return action_method(*args, **kwargs)
        else:
            raise InvalidActionError(action_name)

    def eval(self, soln: Any, trace: list[SessionItem], duration: float):
        self.add_result("TTA", duration)
        self.common_eval(trace)
        return self.results
