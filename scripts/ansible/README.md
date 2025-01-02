## Environment Setup

This is the instruction to use Ansible to build environment including, the K8S cluster, the TiDB operator. We use the CloudLab VMs as an example. Note that the current setup is only for on-cluster management. We will support the remote cluster management in the future.

### Exchange SSH keys

The nodes should exchange their public keys with each other before running Ansible.
In the machine that can access all the VMs (e.g., your laptop whose key has been stored in CloudLab), 
modify the `ssh/hosts.txt` file to record down IPs/hostnames of the nodes.
Then run the following commands:

```shell
cd ssh
./keys.sh
```

### Install Ansible (Ubuntu)

SSH into one of the nodes as controller node: `ssh <USER_NAME>@<HOST>`

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


<!-- 
### SSH keys (optional)

Generate ssh key in the controller node, e.g.,:
```shell
ssh-keygen -t rsa -b 4096 -C "yinfang3@illinois.edu"
```

Then add the key to the authorized_keys files of other nodes.

You can also modify the `hosts.txt` and use the `keys.sh` in the `ssh` dir to automatically do this.
