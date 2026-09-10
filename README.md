# DevOps EKS Lab

An educational project that provisions an ephemeral Amazon EKS
environment with Terraform and deploys a Python FastAPI application
through Azure Pipelines.

## Status

Work in progress: repository setup and project foundations.

## Architecture

- Source control: Azure Repos.
- CI/CD: Azure Pipelines.
- Cloud: AWS, us-east-1.
- Infrastructure as code: Terraform.
- Container registry: Amazon ECR.
- Container orchestration: Amazon EKS.
- Application: Python and FastAPI.
- Deployment packaging: Helm.
- Portfolio: GitHub mirror of the Azure repository.

## Planned application

A task-management API with CRUD operations, health checks,
readiness checks, and metrics.

## Planned governance

- Pull requests and protected branches.
- Automated validation before merging.
- Deployment approvals.
- Separate AWS roles for pipeline responsibilities.
- Federated pipeline authentication through OIDC.

These controls will be implemented and verified during the lab.

## Environment lifecycle

Provision infrastructure, deploy the application, test for up to
15 minutes, and destroy the ephemeral resources.

Provisioning and deletion require additional time.
Persistent bootstrap resources are managed separately.

## Cost target

A monthly AWS budget alert threshold of USD 3.

Budget alerts do not enforce a spending limit.
Actual costs will be reviewed before provisioning.

## Repository workflow

Azure Repos is the source of truth.
GitHub will receive a portfolio mirror after changes merge in Azure Repos.