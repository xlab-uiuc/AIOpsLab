import atexit
from aiopslab.orchestrator.orchestrator import Orchestrator, exit_cleanup_fault
from aiopslab.service.apps.hotelres import HotelReservation
from aiopslab.service.helm import Helm
from aiopslab.utils.critical_section import CriticalSection


if __name__ == "__main__":

    orchestrator = Orchestrator()
    orchestrator.register_agent(None, name="gpt-w-shell")

    def hr_deploy(self):
        print(f"Deploying Kubernetes configurations in namespace: {self.namespace}")
        self.kubectl.apply_configs(self.namespace, self.k8s_deploy_path)
    HotelReservation.deploy = hr_deploy
    Helm.assert_if_deployed = lambda x: True

    pid = input("Enter the problem ID: ")
    
    problem_desc, instructs, apis = orchestrator.init_problem(pid)

    
    input("Press Enter to continue...")

    with CriticalSection():
        orchestrator.session.problem.recover_fault()
        atexit.unregister(exit_cleanup_fault)
        
    # Beyond recovering from fault,
    # I feel sometimes it is safer to delete the whole namespace.
    # But this will take more time.
    # if not self.session.problem.sys_status_after_recovery():
    orchestrator.session.problem.app.cleanup()
    orchestrator.prometheus.teardown()
    print("Uninstalling OpenEBS...")
    orchestrator.kubectl.exec_command("kubectl delete sc openebs-hostpath openebs-device --ignore-not-found")
    orchestrator.kubectl.exec_command(
        "kubectl delete -f https://openebs.github.io/charts/openebs-operator.yaml"
    )
    orchestrator.kubectl.wait_for_namespace_deletion("openebs")