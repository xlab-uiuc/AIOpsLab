"""Naive GPT4 client (with shell access) for AIOpsLab.

Achiam, Josh, Steven Adler, Sandhini Agarwal, Lama Ahmad, Ilge Akkaya, Florencia Leoni Aleman, Diogo Almeida et al. 
"Gpt-4 technical report." arXiv preprint arXiv:2303.08774 (2023).

Code: https://openai.com/index/gpt-4-research/
Paper: https://arxiv.org/abs/2303.08774
"""
import os
import asyncio

import wandb
from aiopslab.orchestrator import Orchestrator
from clients.utils.llm import LlamaClient
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

TASK_MESSAGE = """{prob_desc}
You are provided with the following APIs to interact with the service:

{telemetry_apis}

You are also provided an API to a secure terminal to the service where you can run commands:

{shell_api}

Finally, you will submit your solution for this task using the following API:

{submit_api}

At each turn think step-by-step and respond with your action.

IMPORTANT:
1. The submit() call must strictly follow its defined parameter signature for this task.
2. Provide the call in a markdown code block.

At each turn respond with:
Action: <your action>
"""

class Agent:
    def __init__(self):
        self.history = []
        self.llm = LlamaClient()
    
    def test(self):
        return self.llm.run([{"role": "system", "content": "hello"}])

    def init_context(self, problem_desc: str, instructions: str, apis: str):
        """Initialize the context for the agent."""

        self.shell_api = self._filter_dict(apis, lambda k, _: "exec_shell" in k)
        self.submit_api = self._filter_dict(apis, lambda k, _: "submit" in k)
        self.telemetry_apis = self._filter_dict(
            apis, lambda k, _: "exec_shell" not in k and "submit" not in k
        )
        stringify_apis = lambda apis: "\n\n".join(
            [f"{k}\n{v}" for k, v in apis.items()]
        )

        self.system_message = TASK_MESSAGE.format(
            prob_desc=problem_desc,
            telemetry_apis=stringify_apis(self.telemetry_apis),
            shell_api=stringify_apis(self.shell_api),
            submit_api=stringify_apis(self.submit_api),
        )

        print(f"===== System Message ====\n{self.system_message}")


        self.task_message = instructions

        self.history.append({"role": "system", "content": self.system_message})
        self.history.append({"role": "user", "content": self.task_message})

    async def get_action(self, input) -> str:
        if len(input) > 10000:
            input = "[truncated]" + input[-10000:] 
        print(f"===== Orchestrator ====\n{input}")
        """Wrapper to interface the agent with OpsBench.

        Args:
            input (str): The input from the orchestrator/environment.

        Returns:
            str: The response from the agent.
        """
        self.history.append({"role": "user", "content": input})
        response = self.llm.run(self.history)
        print(f"===== Agent (Llama3 70B) ====\n{response}")
        self.history.append({"role": "assistant", "content": response[0]})
        return response[0]

    def _filter_dict(self, dictionary, filter_func):
        return {k: v for k, v in dictionary.items() if filter_func(k, v)}


if __name__ == "__main__":
    print("Running on Llama3 70B, with full tool set.")
    # Load use_wandb from environment variable with a default of False
    use_wandb = os.getenv("USE_WANDB", "false").lower() == "true"
    
    if use_wandb:
        # Initialize wandb running
        wandb.init(project="AIOpsLab", entity="AIOpsLab")

    agent = Agent()

    orchestrator = Orchestrator()
    orchestrator.register_agent(agent, name="gpt-w-shell")

    pid = os.getenv("TASK_NAME", "misconfig_app_hotel_res-mitigation-1")
    problem_desc, instructs, apis = orchestrator.init_problem(pid)
    agent.init_context(problem_desc, instructs, apis)
    asyncio.run(orchestrator.start_problem(max_steps=30))

    if use_wandb:
        # Finish the wandb run
        wandb.finish()

    agent.llm.print_usage()