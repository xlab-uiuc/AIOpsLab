#!/usr/bin/env python3
import json
from pathlib import Path
import traceback
import tiktoken

from aiopslab.orchestrator.problems.registry import ProblemRegistry
import os

AGENT_MODEL="gpt-4o"
SHOW_PROMPT = True
DOCS_SHELL_ONLY = """{prob_desc}
You are provided with a direct API to a secure terminal to the service where you can run commands:

{shell_api}

Finally, you will submit your solution for this task using the following API:

{submit_api}

IMPORTANT:
1. The submit() call must strictly follow its defined parameter signature for this task.
2. Provide the call in a markdown code block.

At each turn respond with:
Action: <your action>
"""
end_text = ""
read_next_fd = None
results_dir = "./aiopslab/data/results"
session_results = os.listdir(results_dir)

def truncate(text):
    """Truncate the text to a maximum of 10000 characters."""
    if len(text) > 10000:
        return "[truncated]" + text[-10000:]
    return text

def read_next(end_set):
    result = ""
    try:
        while True:
            line = read_next_fd.readline()
            if not line:
                raise EOFError("End of file reached.")
            if any(end in line for end in end_set):
                global end_text
                end_text = line
                break
            result += line + "\n"
    except EOFError:
        raise EOFError("End of file reached.")
    return result

class Cache:
    """A simple cache implementation to store the results of the LLM inference."""

    def __init__(self) -> None:
        self.cache_dict = {}

    @staticmethod
    def process_payload(payload):
        if isinstance(payload, (list, dict)):
            return json.dumps(payload)
        return payload

    def get_from_cache(self, payload):
        payload_cache = self.process_payload(payload)
        if payload_cache in self.cache_dict:
            return self.cache_dict[payload_cache]
        return None

    def add_to_cache(self, payload, output):
        payload_cache = self.process_payload(payload)
        self.cache_dict[payload_cache] = output

    def save_cache(self):
        pass

class MimicClient:
    """Abstraction for OpenAI's GPT series model."""

    def __init__(self):
        self.cache = Cache()
        self.tokenizer = None
    
    def count_message_tokens(self, messages, model):
        if "gpt" in model:
            encoding = tiktoken.encoding_for_model(model)

            tokens_per_message = 3
            tokens_per_name = 1
            total_tokens = 0
            for msg in messages:
                total_tokens += tokens_per_message
                for key, value in msg.items():
                    total_tokens += len(encoding.encode(value))
                    if key == "name":
                        total_tokens += tokens_per_name
            
            if len(messages) == 1 and messages[0]["role"] == "assistant":
                total_tokens -= 3
        else:
            if self.tokenizer is None:
                from transformers import AutoTokenizer
                self.tokenizer = AutoTokenizer.from_pretrained("./llama")

            prompt = self.tokenizer.apply_chat_template(messages, tokenize=True)
            
            total_tokens = len(prompt)

            # Empirically determined
            if len(messages) == 1 and messages[0]["role"] == "assistant":
                total_tokens -= 5
            else:
                total_tokens += 24
        return total_tokens

    def inference(self, payload: list[dict[str, str]]) -> list[str]:
        if self.cache is not None:
            cache_result = self.cache.get_from_cache(payload)
            if cache_result is not None:
                return cache_result
        
        return self.count_message_tokens(messages=payload, model=AGENT_MODEL)

    def run(self, payload: list[dict[str, str]]) -> list[str]:
        response = self.inference(payload)
        if self.cache is not None:
            self.cache.add_to_cache(payload, response)
            self.cache.save_cache()
        return response

class Agent:
    def __init__(self):
        self.history = []
        self.token_in = 0
        self.token_out = 0
        self.client = MimicClient()

    def init_context(self, problem_desc: str, instructions: str, apis: str):
        """Initialize the context for the agent."""

        self.shell_api = self._filter_dict(apis, lambda k, _: "exec_shell" in k)
        self.submit_api = self._filter_dict(apis, lambda k, _: "submit" in k)
        stringify_apis = lambda apis: "\n\n".join(
            [f"{k}\n{v}" for k, v in apis.items()]
        )

        if SHOW_PROMPT:
            read_next(["===== System Message ===="])
            self.system_message = read_next(["===== Orchestrator ===="])
        else:
            self.system_message = DOCS_SHELL_ONLY.format(
                prob_desc=problem_desc,
                shell_api=stringify_apis(self.shell_api),
                submit_api=stringify_apis(self.submit_api),
            )
            read_next(["===== Orchestrator ===="])

        self.task_message = instructions

        self.history.append({"role": "system", "content": self.system_message})
        self.history.append({"role": "user", "content": self.task_message})

    def get_action(self, prompt, response):
        self.history.append({"role": "user", "content": prompt})
        self.token_in += self.count_tokens(self.history)
        self.token_out += self.count_tokens([{"role": "assistant", "content": response}])
        self.history.append({"role": "assistant", "content": response})

    def count_tokens(self, history):
        """Count the number of tokens in the conversation history."""
        return self.client.run(history)

    def _filter_dict(self, dictionary, filter_func):
        return {k: v for k, v in dictionary.items() if filter_func(k, v)}

def disable_creation():
    from aiopslab.service.apps.socialnet import SocialNetwork
    SocialNetwork.create_namespace = lambda self: None
    SocialNetwork.create_tls_secret = lambda self: None
    SocialNetwork.create_configmaps = lambda self: None
    from aiopslab.service.apps.hotelres import HotelReservation
    HotelReservation.create_namespace = lambda self: None
    HotelReservation.create_tls_secret = lambda self: None
    HotelReservation.create_configmaps = lambda self: None
    from aiopslab.service.apps.astronomy_shop import AstronomyShop
    AstronomyShop.create_namespace = lambda self: None
    AstronomyShop.create_tls_secret = lambda self: None
    AstronomyShop.create_configmaps = lambda self: None
    from aiopslab.generators.fault.inject_symp import SymptomFaultInjector
    SymptomFaultInjector.__init__ = lambda self, namespace: None


def init_problem(problem_id: str):
    # Start timer
    probs = ProblemRegistry()
    for problem in probs.get_problem_ids():
        if problem in problem_id:
            problem_id = problem
            break
    prob = probs.get_problem_instance(problem_id)

    task_desc = prob.get_task_description()
    instructions = prob.get_instructions()
    actions = prob.get_available_actions()

    return task_desc, instructions, actions

def conclude(filename):
    global read_next_fd
    read_next_fd = open(filename, "r")
    read_next(["Session ID: "])
    sessionID = end_text.split(": ")[1].strip()
    agent = Agent()
    task_desc, instructions, actions = init_problem(filename)
    agent.init_context(
        task_desc, instructions, actions
    )
    read_next_fd.close()
    
    matching_files = [f for f in session_results if f.startswith(sessionID)]

    if len(matching_files) == 0:
        raise RuntimeError("No matching session files found.")
    
    with open(os.path.join(results_dir, matching_files[0]), "r") as f:
        result = f.read()
        result_parsed = json.loads(result)

    action_list = result_parsed["trace"]
    last_action = "Please take the next action"
    for idx in range(0, len(action_list), 2):
        agent.get_action(last_action, action_list[idx]["content"])
        last_action = truncate(action_list[idx + 1]["content"] + "\n" + "Please take the next action")
        
    results = result_parsed["results"]
    results.update(
        {
            "agent_in_token": agent.token_in,
            "agent_out_token": agent.token_out,
        }
    )

    return results


registry = [
"k8s_target_port-misconfig-detection-1",
"k8s_target_port-misconfig-localization-1",
"k8s_target_port-misconfig-analysis-1",
"k8s_target_port-misconfig-mitigation-1",
"k8s_target_port-misconfig-detection-2",
"k8s_target_port-misconfig-localization-2",
"k8s_target_port-misconfig-analysis-2",
"k8s_target_port-misconfig-mitigation-2",
"k8s_target_port-misconfig-detection-3",
"k8s_target_port-misconfig-localization-3",
"k8s_target_port-misconfig-analysis-3",
"k8s_target_port-misconfig-mitigation-3",
"auth_miss_mongodb-detection-1",
"auth_miss_mongodb-localization-1",
"auth_miss_mongodb-analysis-1",
"auth_miss_mongodb-mitigation-1",
"revoke_auth_mongodb-detection-1",
"revoke_auth_mongodb-localization-1",
"revoke_auth_mongodb-analysis-1",
"revoke_auth_mongodb-mitigation-1",
"revoke_auth_mongodb-detection-2",
"revoke_auth_mongodb-localization-2",
"revoke_auth_mongodb-analysis-2",
"revoke_auth_mongodb-mitigation-2",
"user_unregistered_mongodb-detection-1",
"user_unregistered_mongodb-localization-1",
"user_unregistered_mongodb-analysis-1",
"user_unregistered_mongodb-mitigation-1",
"user_unregistered_mongodb-detection-2",
"user_unregistered_mongodb-localization-2",
"user_unregistered_mongodb-analysis-2",
"user_unregistered_mongodb-mitigation-2",
"misconfig_app_hotel_res-detection-1",
"misconfig_app_hotel_res-localization-1",
"misconfig_app_hotel_res-analysis-1",
"misconfig_app_hotel_res-mitigation-1",
"scale_pod_zero_social_net-detection-1",
"scale_pod_zero_social_net-localization-1",
"scale_pod_zero_social_net-analysis-1",
"scale_pod_zero_social_net-mitigation-1",
"assign_to_non_existent_node_social_net-detection-1",
"assign_to_non_existent_node_social_net-localization-1",
"assign_to_non_existent_node_social_net-analysis-1",
"assign_to_non_existent_node_social_net-mitigation-1",
"container_kill-detection",
"container_kill-localization",
"pod_failure_hotel_res-detection-1",
"pod_failure_hotel_res-localization-1",
"pod_kill_hotel_res-detection-1",
"pod_kill_hotel_res-localization-1",
"network_loss_hotel_res-detection-1",
"network_loss_hotel_res-localization-1",
"network_delay_hotel_res-detection-1",
"network_delay_hotel_res-localization-1",
"noop_detection_hotel_reservation-1",
"noop_detection_social_network-1",
"noop_detection_astronomy_shop-1",
"astronomy_shop_ad_service_failure-detection-1",
"astronomy_shop_ad_service_failure-localization-1",
"astronomy_shop_ad_service_high_cpu-detection-1",
"astronomy_shop_ad_service_high_cpu-localization-1",
"astronomy_shop_ad_service_manual_gc-detection-1",
"astronomy_shop_ad_service_manual_gc-localization-1",
"astronomy_shop_cart_service_failure-detection-1",
"astronomy_shop_cart_service_failure-localization-1",
"astronomy_shop_image_slow_load-detection-1",
"astronomy_shop_image_slow_load-localization-1",
"astronomy_shop_kafka_queue_problems-detection-1",
"astronomy_shop_kafka_queue_problems-localization-1",
"astronomy_shop_payment_service_failure-detection-1",
"astronomy_shop_payment_service_failure-localization-1",
"astronomy_shop_payment_service_unreachable-detection-1",
"astronomy_shop_payment_service_unreachable-localization-1",
"astronomy_shop_product_catalog_service_failure-detection-1",
"astronomy_shop_product_catalog_service_failure-localization-1",
"astronomy_shop_recommendation_service_cache_failure-detection-1",
"astronomy_shop_recommendation_service_cache_failure-localization-1",
"redeploy_without_PV-detection-1",
"redeploy_without_PV-analysis-1",
"redeploy_without_PV-mitigation-1",
"wrong_bin_usage-detection-1",
"wrong_bin_usage-localization-1",
"wrong_bin_usage-analysis-1",
"wrong_bin_usage-mitigation-1",
"astronomy_shop_loadgenerator_flood_homepage-detection-1",
"astronomy_shop_loadgenerator_flood_homepage-localization-1",
]

if __name__ == "__main__":
    disable_creation()
    result_list = []
    result_files = os.listdir("eval")
    for problem in registry:
        try:
            selected = [f for f in result_files if problem in f]
            selected.sort()
            if len(selected) == 0:
                print(f"No results found for {problem}")
                continue
            newest_file = selected[-1]
            if len(selected) > 0:
                print("Selections:", selected)
            print(f"Processing file: {newest_file}", flush=True)
            result = conclude(os.path.join("eval", newest_file, "run.log"))
            result.update({"problem": problem})
            result_list.append(result)
            print(f"Result: {result}", flush=True)
        except Exception as e:
            tb = "".join(traceback.format_exception(type(e), e, e.__traceback__))
            print(f"Error processing {problem}: {tb}")
    print("Parsed all the problems", flush=True)
    with open("results.json", "w") as f:
        json.dump(result_list, f, indent=4)
