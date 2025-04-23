# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

"""Session wrapper to manage the an agent's session with the orchestrator."""

import time
import uuid
import json
import wandb
from pydantic import BaseModel

# from aiopslab.orchestrator.tasks.base import Task
from aiopslab.paths import RESULTS_DIR


class SessionItem(BaseModel):
    role: str  # system / user / assistant
    content: str


class Session:
    def __init__(self) -> None:
        self.session_id = uuid.uuid4()
        self.pid: str | None = None
        self.problem = None
        self.mutables: set[str] = set()
        self.solution = None
        self.results = {}
        self.history: list[SessionItem] = []
        self.start_time = None
        self.end_time = None
        self.agent_name: str | None = None

    def set_problem(self, problem, pid: str | None = None):
        """Set the problem instance for the session.

        Args:
            problem (Task): The problem instance to set.
            pid (str): The problem ID.
        """
        self.problem = problem
        self.namespace = problem.namespace
        self.pid = pid

    def set_solution(self, solution):
        """Set the solution shared by the agent.

        Args:
            solution (Any): The solution instance to set.
        """
        self.solution = solution

    def set_results(self, results):
        """Set the results of the session.

        Args:
            results (Any): The results of the session.
        """
        self.results = results

    def set_agent(self, agent_name):
        """Set the agent name for the session.

        Args:
            agent_name (str): The name of the agent.
        """
        self.agent_name = agent_name

    def add_mutables(self, elements: list[str]):
        """Add mutable elements under the given namespace

        Args:
            element (str): The mutable element
        """
        self.mutables = self.mutables.union(set(elements))

    def add(self, item: SessionItem | dict | list):
        """Add an item into the session history.

        Args:
            item: The item to inject into the session history.
        """
        if not item:
            return

        if isinstance(item, SessionItem):
            self.history.append(item)
        elif isinstance(item, dict):
            self.history.append(SessionItem.model_validate(item))
        elif isinstance(item, list):
            for sub_item in item:
                self.add(sub_item)
        else:
            raise TypeError("Unsupported type %s" % type(item))

    def clear(self):
        """Clear the session history."""
        self.history = []

    def start(self):
        """Start the session."""
        self.start_time = time.time()

    def end(self):
        """End the session."""
        self.end_time = time.time()

    def get_duration(self) -> float:
        """Get the duration of the session."""
        duration = self.end_time - self.start_time
        return duration

    def to_dict(self):
        """Return the session history as a dictionary."""
        summary = {
            "agent": self.agent_name,
            "session_id": str(self.session_id),
            "problem_id": self.pid,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "mutables": ",".join(self.mutables or []),
            "trace": [item.model_dump() for item in self.history],
            "results": self.results,
        }

        return summary

    def to_json(self):
        """Save the session to a JSON file."""
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)

        with open(RESULTS_DIR / f"{self.session_id}_{self.start_time}.json", "w") as f:
            json.dump(self.to_dict(), f, indent=4)
    
    def to_wandb(self):
        """Log the session to Weights & Biases."""
        wandb.log(self.to_dict())

    def from_json(self, filename: str):
        """Load a session from a JSON file."""

        with open(RESULTS_DIR / filename, "r") as f:
            data = json.load(f)

        self.session_id = data.get("session_id")
        self.start_time = data.get("start_time")
        self.end_time = data.get("end_time")
        self.results = data.get("results")
        self.history = [SessionItem.model_validate(item) for item in data.get("trace")]
