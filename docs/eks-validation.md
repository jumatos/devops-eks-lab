# EKS validation

Validation date: 2026-09-16 (UTC)

## Infrastructure

- Cluster: `devops-eks-lab`.
- Kubernetes version: `1.36`.
- Region: `us-east-1`.
- Managed node group: `lab`.
- Node type: `t3.medium`, On-Demand.
- Node operating system: Amazon Linux 2023.
- Nodes run in private subnets without public IP addresses.
- Private API endpoint enabled.
- Public API endpoint restricted to the administrator CIDR.
- Terraform state stored in S3 with native locking.
- A single NAT Gateway provides outbound connectivity for the lab.

## EKS add-ons

The following managed add-ons were installed and reported `ACTIVE`:

- Amazon VPC CNI.
- kube-proxy.
- CoreDNS.
- EKS Pod Identity Agent.

## Workload identity

The `task-api` workload uses:

- Kubernetes namespace: `task-api`.
- Kubernetes ServiceAccount: `task-api`.
- IAM role: `devops-eks-lab-task-api`.
- EKS Pod Identity association.
- IAM access restricted to the `devops-eks-lab-tasks` DynamoDB table.

No static AWS access keys are stored in the Helm chart or Kubernetes Secret.

## Application deployment

The Helm release `task-api` was deployed using the immutable ECR image:

```text
703671937762.dkr.ecr.us-east-1.amazonaws.com/devops-eks-lab-api:sha-7df7c14fdb18-build-35-attempt-1