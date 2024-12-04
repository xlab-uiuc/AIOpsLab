# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""Define and query information about an AIOps Detection task."""

import textwrap
from typing import Any


from aiopslab.orchestrator.tasks.base import Task
from aiopslab.orchestrator.actions.detection import DetectionActions
from aiopslab.service.apps.base import Application
from aiopslab.session import SessionItem
from aiopslab.utils.actions import get_actions
from aiopslab.utils.status import InvalidActionError


class DetectionTask(Task):
    """An AIOps anomaly detection task."""

    def __init__(self, app: Application):
        super().__init__()
        self.app = app
        self.helm_configs = self.app.helm_configs
        self.app_summary = self.app.get_app_summary()
        self.actions = DetectionActions()

        self.task_desc = """\
            You are an expert DevOps engineer who has been tasked with detecting anomalies in a deployed service.

            The service you are working with today is described below:
            {app_summary}

            You will begin by analyzing the service's state and telemetry, and then submit your solution:
            1. str: `Yes` or `No` to indicate whether there are anomalies detected
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
        return get_actions(task="detection")

    def perform_action(self, action_name, *args, **kwargs):
        action_method = getattr(self.actions, action_name, None)

        if action_method is not None and callable(action_method):
            return action_method(*args, **kwargs)
        else:
            raise InvalidActionError(action_name)

    def eval(self, soln: Any, trace: list[SessionItem], duration: float):
        self.add_result("TTD", duration)
        self.common_eval(trace)
        return self.results
