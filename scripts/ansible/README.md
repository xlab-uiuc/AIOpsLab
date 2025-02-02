## Environment Setup

This is the instruction to use Ansible to build a remote cluster for AIOpsLab. We currently use [CloudLab](https://www.cloudlab.us/) but we believe this will work on any servers you have access to.

### Exchange SSH keys (Optional)

Your nodes need to be able to ssh into each other to setup the cluster. If your nodes have different keys then the device you're running AIOpsLab on, or if you're unsure, proceed with the following steps to exchange ssh keys between the nodes.

The nodes should exchange their public keys with each other before running Ansible.
In the machine that can access all the VMs (e.g., your laptop whose key has been stored in CloudLab), 
modify the `ssh/hosts.txt` file to record down IPs/hostnames of the nodes.
Then run the following commands:

```shell
cd ssh
./keys.sh
```

### Install Ansible (Ubuntu)

SSH into your desired control node: `ssh <USER_NAME>@<HOST>`

Then run:
```shell
sudo apt update && sudo apt upgrade -y
sudo apt install software-properties-common

sudo add-apt-repository --yes --update ppa:ansible/ansible

#Install Ansible
sudo apt install ansible -y

#Validate Ansible:
ansible --version 
```

Once those commands have completed, you can exit the SSH session.

### Modify the inventory file
 
Modify the IPs and user names in the inventory file accordingly, `inventory.yml`. You can get the control plane IP by running `hostname -I` in the control plane node.

### Run the Ansible playbook

Install some common requirements (e.g., package installation) in all of the nodes; and setup the controllers and workers to run K8S:
```shell
ansible-playbook -i inventory.yml setup_common.yml && ansible-playbook -i inventory.yml setup_controller_worker.yml
```

After these, you should see every node running inside a K8S cluster:
```shell
kubectl get nodes
```

### Common Errors
If you're running into issues from Ansible related to host key authentication, try typing `yes` in your terminal for each node, or proceeding with the following steps:

You can create a file in the same directory as this README called `ansible.cfg` to turn off that warning:
```yaml
[defaults]
host_key_checking = False
```
Be mindful about the security implications of disabling host key checking, if you're not aware ask someone who is.
