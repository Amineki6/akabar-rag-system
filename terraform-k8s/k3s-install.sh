#!/bin/bash

# 1. Install K3s (Lightweight Kubernetes)
# We export INSTALL_K3S_EXEC to configure the K3s service with extra arguments.
# --kubelet-arg=image-gc-high-threshold=75 : Start deleting images when disk is 75% full
# --kubelet-arg=image-gc-low-threshold=60  : Stop deleting when disk drops to 60%
export INSTALL_K3S_EXEC="server --kubelet-arg=image-gc-high-threshold=75 --kubelet-arg=image-gc-low-threshold=60"

curl -sfL https://get.k3s.io | sh -

# 2. Wait for K3s to be ready
echo "Waiting for K3s to start..."
while [ ! -f /etc/rancher/k3s/k3s.yaml ]; do sleep 2; done

# 3. Fix permissions so the 'ubuntu' user can run kubectl commands
chmod 644 /etc/rancher/k3s/k3s.yaml
export KUBECONFIG=/etc/rancher/k3s/k3s.yaml

# 4. Install ArgoCD
# Create the namespace
/usr/local/bin/kubectl create namespace argocd

# Apply the manifest from the official ArgoCD repo
/usr/local/bin/kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

echo "K3s and ArgoCD installation complete."