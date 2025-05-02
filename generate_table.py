

import json


detection_table = [
"k8s_target_port-misconfig-detection-1",
"k8s_target_port-misconfig-detection-2",
"k8s_target_port-misconfig-detection-3",
"auth_miss_mongodb-detection-1",
"revoke_auth_mongodb-detection-1",
"revoke_auth_mongodb-detection-2",
"user_unregistered_mongodb-detection-1",
"user_unregistered_mongodb-detection-2",
"misconfig_app_hotel_res-detection-1",
"scale_pod_zero_social_net-detection-1",
"assign_to_non_existent_node_social_net-detection-1",
"container_kill-detection",
"pod_failure_hotel_res-detection-1",
"pod_kill_hotel_res-detection-1",
"network_loss_hotel_res-detection-1",
"network_delay_hotel_res-detection-1",
"noop_detection_hotel_reservation-1",
"noop_detection_social_network-1",
"astronomy_shop_ad_service_failure-detection-1",
"astronomy_shop_ad_service_high_cpu-detection-1",
"astronomy_shop_ad_service_manual_gc-detection-1",
"astronomy_shop_cart_service_failure-detection-1",
"astronomy_shop_image_slow_load-detection-1",
"astronomy_shop_kafka_queue_problems-detection-1",
"astronomy_shop_payment_service_failure-detection-1",
"astronomy_shop_payment_service_unreachable-detection-1",
"astronomy_shop_product_catalog_service_failure-detection-1",
"astronomy_shop_recommendation_service_cache_failure-detection-1",
"redeploy_without_PV-detection-1",
"wrong_bin_usage-detection-1",
"noop_detection_astronomy_shop-1",
"astronomy_shop_loadgenerator_flood_homepage-detection-1",
]

localization_table = [
"k8s_target_port-misconfig-localization-1",
"k8s_target_port-misconfig-localization-2",
"k8s_target_port-misconfig-localization-3",
"auth_miss_mongodb-localization-1",
"revoke_auth_mongodb-localization-1",
"revoke_auth_mongodb-localization-2",
"user_unregistered_mongodb-localization-1",
"user_unregistered_mongodb-localization-2",
"misconfig_app_hotel_res-localization-1",
"scale_pod_zero_social_net-localization-1",
"assign_to_non_existent_node_social_net-localization-1",
"container_kill-localization",
"pod_failure_hotel_res-localization-1",
"pod_kill_hotel_res-localization-1",
"network_loss_hotel_res-localization-1",
"network_delay_hotel_res-localization-1",
"astronomy_shop_ad_service_failure-localization-1",
"astronomy_shop_ad_service_high_cpu-localization-1",
"astronomy_shop_ad_service_manual_gc-localization-1",
"astronomy_shop_cart_service_failure-localization-1",
"astronomy_shop_image_slow_load-localization-1",
"astronomy_shop_kafka_queue_problems-localization-1",
"astronomy_shop_payment_service_failure-localization-1",
"astronomy_shop_payment_service_unreachable-localization-1",
"astronomy_shop_product_catalog_service_failure-localization-1",
"astronomy_shop_recommendation_service_cache_failure-localization-1",
"wrong_bin_usage-localization-1",
"astronomy_shop_loadgenerator_flood_homepage-localization-1",
]

analysis_table = [
"k8s_target_port-misconfig-analysis-1",
"k8s_target_port-misconfig-analysis-2",
"k8s_target_port-misconfig-analysis-3",
"assign_to_non_existent_node_social_net-analysis-1",
"scale_pod_zero_social_net-analysis-1",
"user_unregistered_mongodb-analysis-1",
"user_unregistered_mongodb-analysis-2",
"revoke_auth_mongodb-analysis-1",
"revoke_auth_mongodb-analysis-2",
"auth_miss_mongodb-analysis-1",
"misconfig_app_hotel_res-analysis-1",
"redeploy_without_PV-analysis-1",
"wrong_bin_usage-analysis-1",
]

mitigation_table = [
"k8s_target_port-misconfig-mitigation-1",
"k8s_target_port-misconfig-mitigation-2",
"k8s_target_port-misconfig-mitigation-3",
"assign_to_non_existent_node_social_net-mitigation-1",
"scale_pod_zero_social_net-mitigation-1",
"user_unregistered_mongodb-mitigation-1",
"user_unregistered_mongodb-mitigation-2",
"revoke_auth_mongodb-mitigation-1",
"revoke_auth_mongodb-mitigation-2",
"auth_miss_mongodb-mitigation-1",
"misconfig_app_hotel_res-mitigation-1",
"redeploy_without_PV-mitigation-1",
"wrong_bin_usage-mitigation-1"
]

if __name__ == "__main__":
    with open("results.json", "r") as f:
        content = json.loads(f.read())

    B = lambda x: 'TRUE' if x else 'FALSE'
    # generate for detection table
    with open("detection_table.csv", "w") as f:
        for task in detection_table:
            entry = [x for x in content if task in x["problem"]][0]
            # time, steps, max_steps, in_tokens, out_tokens
            print(f"{entry["TTD"]}, {entry["steps"]}, 30, {entry["agent_in_token"]}, {entry["agent_out_token"]}, {B(entry["Detection Accuracy"] == "Correct")}", file=f)
    with open("localization_table.csv", "w") as f:
        for task in localization_table:
            entry = [x for x in content if task in x["problem"]][0]
            print(f"{entry["TTL"]}, {entry["steps"]}, 30, {entry["agent_in_token"]}, {entry["agent_out_token"]}, {B(entry["success"])}, {entry["Localization Accuracy"]}, {entry["TTL"]}", file=f)

    with open("analysis_table.csv", "w") as f:
        for task in analysis_table:
            entry = [x for x in content if task in x["problem"]][0]
            print(f"{entry["TTA"]}, {entry["steps"]}, 30, {entry["agent_in_token"]}, {entry["agent_out_token"]}, {B(entry["success"])}, {B(entry["system_level_correct"])}, {B(entry["fault_type_correct"])}", file=f)

    with open("mitigation_table.csv", "w") as f:
        # time	steps 	max_steps	total_tokens	prompt_tokens	success	workload time
        for task in mitigation_table:
            entry = [x for x in content if task in x["problem"]][0]
            print(f"{entry["TTM"]}, {entry["steps"]}, 30, {entry["agent_in_token"] + entry["agent_out_token"]}, {entry["agent_in_token"]}, {entry["success"]}", file=f)