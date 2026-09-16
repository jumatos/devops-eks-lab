# Network validation

Validation date: 2026-09-16 (UTC)

## Configuration

- Region: us-east-1.
- VPC CIDR: 10.20.0.0/16.
- Availability Zones: us-east-1a and us-east-1b.
- Public subnets: 10.20.0.0/24 and 10.20.1.0/24.
- Private subnets: 10.20.16.0/20 and 10.20.32.0/20.
- DNS support and DNS hostnames enabled.
- Public route table uses an Internet Gateway.
- Each private subnet has its own route table.
- Automatic public IPv4 assignment disabled.
- Subnets tagged for public and internal load balancer discovery.

## Validation

- Terraform validate passed.
- Apply completed: 14 added, 0 changed, 0 destroyed.
- Subsequent plan returned No changes.
- State backend: S3, key network/terraform.tfstate.
- Native S3 state locking enabled.

## Current limitations

- NAT Gateway is disabled.
- No Elastic IP was allocated by this configuration.
- Private subnets currently have no internet egress.
- EKS and worker nodes have not been created.
- Workload connectivity has not yet been tested.
- Optional NAT configuration uses one gateway in us-east-1a:
  private internet egress would depend on that Availability Zone.
