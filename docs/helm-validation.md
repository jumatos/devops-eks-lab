# Helm and Minikube validation

Validation date: 2026-09-16 (UTC)

## Environment

- Helm: 4.3.0.
- Minikube Kubernetes: 1.35.1.
- Namespace and release: task-api.
- Chart: charts/task-api.
- Image: devops-eks-lab-api:trixie, loaded into Minikube.
- Local image pull policy: Never.
- DynamoDB table: devops-eks-lab-tasks in us-east-1.

## Validation results

- Helm lint passed.
- Helm templates rendered successfully.
- Helm installation and upgrade succeeded.
- Without AWS credentials, readiness returned 503.
- With temporary credentials, the Pod reached 1/1 Ready.
- Health and readiness returned 200 through port-forward on port 8004.
- CRUD against real DynamoDB passed:
  - Create.
  - Get by ID.
  - List.
  - Update and subsequent read.
  - Delete.
  - Get after deletion returned 404.
- The test task was deleted.

## AWS access

- Role: devops-eks-lab-local-api.
- Permissions limited to GetItem, PutItem, UpdateItem, DeleteItem
  and Scan on the task table.
- Temporary STS credentials are supplied through an existing Secret.
- scripts/refresh-minikube-aws.sh renews credentials and restarts
  the Deployment.
- Credentials expire after one hour and are not renewed automatically.
- Credential values are not stored in Git or Helm values.

## Deployment configuration

- Non-root UID/GID 10001.
- Read-only root filesystem.
- Privilege escalation disabled and all capabilities dropped.
- RuntimeDefault seccomp profile.
- Memory-backed temporary volume.
- CPU and memory requests and limits.
- Separate startup, liveness and readiness probes.

## Scope

Validation was performed on Minikube.
EKS deployment and workload identity remain pending.
