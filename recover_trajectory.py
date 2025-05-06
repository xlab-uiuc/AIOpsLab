
import datetime
import json
import os
from pathlib import Path

from aiopslab.orchestrator.problems.registry import ProblemRegistry
from clients.utils.templates import DOCS

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
    eval_dir = input("Enter the evaluation directory: ")
    result_list = []
    result_files = os.listdir(os.path.join(eval_dir, "result_jsons"))
    base_dir = Path(eval_dir).parent
    results_dir = os.path.join(base_dir, "aiopslab", "data", "results")
    session_result_files = os.listdir(results_dir)
    session_results = []

    for session_result_file in session_result_files:
        session_result_path = os.path.join(results_dir, session_result_file)
        with open(session_result_path, "r") as f:
            parsed = json.load(f)
            session_results.append(parsed)

    def _filter_dict(dictionary, filter_func):
        return {k: v for k, v in dictionary.items() if filter_func(k, v)}
    
    def make_up_trajectory(session_result):
        origin_timestamp = session_result["start_time"]
        dt_object = datetime.datetime.fromtimestamp(origin_timestamp)
        timestamp = dt_object.strftime("%m-%d_%H-%M-%S")
        mimic_dir = os.path.join(eval_dir, f"{timestamp}-{session_result['problem_id']}")
        os.makedirs(mimic_dir, exist_ok=True)

        with open(os.path.join(mimic_dir, "run.log"), "w") as f:
            print(f"Running on {session_result['problem_id']}", file=f)
            print(f"Session ID: {session_result['session_id']}", file=f)

            task_desc, instructions, actions = init_problem(session_result['problem_id'])

            shell_api = _filter_dict(actions, lambda k, _: "exec_shell" in k)
            submit_api = _filter_dict(actions, lambda k, _: "submit" in k)
            telemetry_apis = _filter_dict(
                actions, lambda k, _: "exec_shell" not in k and "submit" not in k
            )

            stringify_apis = lambda apis: "\n\n".join(
                [f"{k}\n{v}" for k, v in apis.items()]
            )

            # system_message = f"""
            # Problem Description: {task_desc}

            # Available Telemetry APIs:
            # {stringify_apis(telemetry_apis)}

            # Shell API:
            # {stringify_apis(shell_api)}

            # Submit API:
            # {stringify_apis(submit_api)}
            # """
            # system_message = TASK_MESSAGE.format(
            #     prob_desc=task_desc,
            #     telemetry_apis=stringify_apis(telemetry_apis),
            #     shell_api=stringify_apis(shell_api),
            #     submit_api=stringify_apis(submit_api),
            # )

            system_message = DOCS.format(
                prob_desc=task_desc,
                telemetry_apis=stringify_apis(telemetry_apis),
                shell_api=stringify_apis(shell_api),
                submit_api=stringify_apis(submit_api),
            )

            print(f"===== System Message ====\n{system_message}", file=f)

            print(f"===== Orchestrator ====\nPlease take the next action", file=f)

            for action in session_result["trace"]:
                if action["role"] == "env":
                    print(f"===== Orchestrator ====\n{action['content']}", file=f)
                elif action["role"] == "assistant":
                    print(f"===== Agent (React) ====\n{action['content']}", file=f)
            
            print(f"== Evaluation ==\nResults:\n{session_result['results']}", file=f)
        
        # input("Press Enter to continue...")
    
    total_generated = 0
    for result_file in result_files:
        result_path = os.path.join(eval_dir, "result_jsons", result_file)
        with open(result_path, "r") as f:
            parsed = json.load(f)
            matched = False
            for session_result in session_results:
                if parsed == session_result["results"]:
                    print(f"Matched {result_file} with {session_result['session_id']}")
                    make_up_trajectory(session_result)
                    matched = True
                    break
            if not matched:
                print(f"Session result not found for {result_file}")
            else:
                total_generated += 1
                # input("Press Enter to continue...")
    print("Total generated:", total_generated)
    print("Total files found:", len(result_files))