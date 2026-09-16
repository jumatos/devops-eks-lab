# Argo CD GitOps validation

Validation date: 2026-09-16

## Configuration

- EKS cluster: `devops-eks-lab`.
- Argo CD chart: `argo/argo-cd` version `10.9.1`.
- Argo CD application version: `v3.5.3`.
- Git repository: `https://github.com/jumatos/devops-eks-lab.git`.
- Tracked revision: `main`.
- Helm chart path: `charts/task-api`.
- Destination namespace: `task-api`.
- Argo CD service type: `ClusterIP`.

Dex, Notifications and ApplicationSet are disabled because they are not
required by this lab.

## Install or restore Argo CD

```bash
helm repo add argo https://argoproj.github.io/argo-helm
helm repo update

helm upgrade --install argocd argo/argo-cd \
  --kube-context devops-eks-lab \
  --namespace argocd \
  --create-namespace \
  --version 10.9.1 \
  --values gitops/argocd/values.yaml \
  --wait \
  --timeout 10m