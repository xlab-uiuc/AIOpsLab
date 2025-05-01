sudo kubeadm reset -f --cri-socket=unix:///var/run/cri-dockerd.sock
sudo iptables -F
sudo iptables -t nat -F
sudo iptables -t mangle -F
sudo iptables -X
sudo ip link delete cni0
sudo rm -rf /etc/cni/net.d
sudo rm -rf /var/lib/cni/
sudo rm -rf /var/lib/kubelet/*
sudo rm -rf /var/lib/etcd
sudo rm -rf /etc/kubernetes/
rm -rf ~/.kube
