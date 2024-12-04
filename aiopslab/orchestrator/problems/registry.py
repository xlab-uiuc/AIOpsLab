# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.

from aiopslab.orchestrator.problems.k8s_target_port_misconfig import *
from aiopslab.orchestrator.problems.auth_miss_mongodb import *
from aiopslab.orchestrator.problems.revoke_auth import *
from aiopslab.orchestrator.problems.storage_user_unregistered import *
from aiopslab.orchestrator.problems.misconfig_app import *
from aiopslab.orchestrator.problems.scale_pod import *
from aiopslab.orchestrator.problems.assign_non_existent_node import *
from aiopslab.orchestrator.problems.pod_failure import *
from aiopslab.orchestrator.problems.network_loss import *
from aiopslab.orchestrator.problems.no_op import *


class ProblemRegistry:
    def __init__(self):
        self.PROBLEM_REGISTRY = {
            # K8s target port misconfig
            "k8s_target_port-misconfig-detection-1": lambda: K8STargetPortMisconfigDetection(faulty_service="user-service"),
            "k8s_target_port-misconfig-localization-1": lambda: K8STargetPortMisconfigLocalization(faulty_service="user-service"),
            "k8s_target_port-misconfig-analysis-1": lambda: K8STargetPortMisconfigAnalysis(faulty_service="user-service"),
            "k8s_target_port-misconfig-mitigation-1": lambda: K8STargetPortMisconfigMitigation(faulty_service="user-service"),
            "k8s_target_port-misconfig-detection-2": lambda: K8STargetPortMisconfigDetection(faulty_service="text-service"),
            "k8s_target_port-misconfig-localization-2": lambda: K8STargetPortMisconfigLocalization(faulty_service="text-service"),
            "k8s_target_port-misconfig-analysis-2": lambda: K8STargetPortMisconfigAnalysis(faulty_service="text-service"),
            "k8s_target_port-misconfig-mitigation-2": lambda: K8STargetPortMisconfigMitigation(faulty_service="text-service"),
            "k8s_target_port-misconfig-detection-3": lambda: K8STargetPortMisconfigDetection(faulty_service="post-storage-service"),
            "k8s_target_port-misconfig-localization-3": lambda: K8STargetPortMisconfigLocalization(faulty_service="post-storage-service"),
            "k8s_target_port-misconfig-analysis-3": lambda: K8STargetPortMisconfigAnalysis(faulty_service="post-storage-service"),
            "k8s_target_port-misconfig-mitigation-3": lambda: K8STargetPortMisconfigMitigation(faulty_service="post-storage-service"),
            # MongoDB auth missing
            "auth_miss_mongodb-detection-1": MongoDBAuthMissingDetection,
            "auth_miss_mongodb-localization-1": MongoDBAuthMissingLocalization,
            "auth_miss_mongodb-analysis-1": MongoDBAuthMissingAnalysis,
            "auth_miss_mongodb-mitigation-1": MongoDBAuthMissingMitigation,
            # MongoDB auth revoke
            "revoke_auth_mongodb-detection-1": lambda: MongoDBRevokeAuthDetection(faulty_service="mongodb-geo"),
            "revoke_auth_mongodb-localization-1": lambda: MongoDBRevokeAuthLocalization(faulty_service="mongodb-geo"),
            "revoke_auth_mongodb-analysis-1": lambda: MongoDBRevokeAuthAnalysis(faulty_service="mongodb-geo"),
            "revoke_auth_mongodb-mitigation-1": lambda: MongoDBRevokeAuthMitigation(faulty_service="mongodb-geo"),
            "revoke_auth_mongodb-detection-2": lambda: MongoDBRevokeAuthDetection(faulty_service="mongodb-rate"),
            "revoke_auth_mongodb-localization-2": lambda: MongoDBRevokeAuthLocalization(faulty_service="mongodb-rate"),
            "revoke_auth_mongodb-analysis-2": lambda: MongoDBRevokeAuthAnalysis(faulty_service="mongodb-rate"),
            "revoke_auth_mongodb-mitigation-2": lambda: MongoDBRevokeAuthMitigation(faulty_service="mongodb-rate"),
            # MongoDB user unregistered
            "user_unregistered_mongodb-detection-1": lambda: MongoDBUserUnregisteredDetection(faulty_service="mongodb-geo"),
            "user_unregistered_mongodb-localization-1": lambda: MongoDBUserUnregisteredLocalization(faulty_service="mongodb-geo"),
            "user_unregistered_mongodb-analysis-1": lambda: MongoDBUserUnregisteredAnalysis(faulty_service="mongodb-geo"),
            "user_unregistered_mongodb-mitigation-1": lambda: MongoDBUserUnregisteredMitigation(faulty_service="mongodb-geo"),
            "user_unregistered_mongodb-detection-2": lambda: MongoDBUserUnregisteredDetection(faulty_service="mongodb-rate"),
            "user_unregistered_mongodb-localization-2": lambda: MongoDBUserUnregisteredLocalization(faulty_service="mongodb-rate"),
            "user_unregistered_mongodb-analysis-2": lambda: MongoDBUserUnregisteredAnalysis(faulty_service="mongodb-rate"),
            "user_unregistered_mongodb-mitigation-2": lambda: MongoDBUserUnregisteredMitigation(faulty_service="mongodb-rate"),
            # App misconfig
            "misconfig_app_hotel_res-detection-1": MisconfigAppHotelResDetection,
            "misconfig_app_hotel_res-localization-1": MisconfigAppHotelResLocalization,
            "misconfig_app_hotel_res-analysis-1": MisconfigAppHotelResAnalysis,
            "misconfig_app_hotel_res-mitigation-1": MisconfigAppHotelResMitigation,
            # Scale pod to zero deployment
            "scale_pod_zero_social_net-detection-1": ScalePodSocialNetDetection,
            "scale_pod_zero_social_net-localization-1": ScalePodSocialNetLocalization,
            "scale_pod_zero_social_net-analysis-1": ScalePodSocialNetAnalysis,
            "scale_pod_zero_social_net-mitigation-1": ScalePodSocialNetMitigation,
            # Assign pod to non-existent node
            "assign_to_non_existent_node_social_net-detection-1": AssignNonExistentNodeSocialNetDetection,
            "assign_to_non_existent_node_social_net-localization-1": AssignNonExistentNodeSocialNetLocalization,
            "assign_to_non_existent_node_social_net-analysis-1": AssignNonExistentNodeSocialNetAnalysis,
            "assign_to_non_existent_node_social_net-mitigation-1": AssignNonExistentNodeSocialNetMitigation,
            # Pod failure
            "pod_failure_hotel_res-detection-1": PodFailureDetection,
            "pod_failure_hotel_res-localization-1": PodFailureLocalization,
            # Network loss
            "network_loss_hotel_res-detection-1": NetworkLossDetection,
            "network_loss_hotel_res-localization-1": NetworkLossLocalization,
            # No operation 
            "noop_detection_hotel_reservation-1": lambda: NoOpDetection(app_name="hotel"),
            "noop_detection_social_network-1": lambda: NoOpDetection(app_name="social"),
        }

    def get_problem_instance(self, problem_id: str):

        if problem_id not in self.PROBLEM_REGISTRY:
            raise ValueError(f"Problem ID {problem_id} not found in registry.")

        return self.PROBLEM_REGISTRY.get(problem_id)()

    def get_problem(self, problem_id: str):
        return self.PROBLEM_REGISTRY.get(problem_id)

    def get_problem_ids(self, task_type: str = None):
        if task_type:
            return [k for k in self.PROBLEM_REGISTRY.keys() if task_type in k]
        return list(self.PROBLEM_REGISTRY.keys())

    def get_problem_count(self, task_type: str = None):
        if task_type:
            return len([k for k in self.PROBLEM_REGISTRY.keys() if task_type in k])
        return len(self.PROBLEM_REGISTRY)
