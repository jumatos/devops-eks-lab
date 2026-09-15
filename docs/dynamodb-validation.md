# DynamoDB validation

Validation date: 2026-09-15

## Infrastructure

- Table: devops-eks-lab-tasks.
- Region: us-east-1.
- Terraform configuration: infra/dynamodb.
- Partition key: id (String).
- No sort key.
- Billing mode: PAY_PER_REQUEST.

## Test environment

- FastAPI running locally through Uvicorn on port 8003.
- Real AWS DynamoDB table.
- Authentication through the local devops-lab SSO profile.
- DYNAMODB_TABLE_NAME loaded from Terraform output.

## Verified behavior

- GET /health returned 200.
- GET /ready returned 200.
- Task creation returned an ID and pending status.
- The same task was retrieved with 200 after restarting Uvicorn.
- PATCH changed the task status to completed and returned 200.
- A subsequent GET confirmed the updated status.
- DELETE returned 204.
- GET after deletion returned 404.
- The test task was deleted.

## Scope

This validates the local API integration with real DynamoDB.
EKS connectivity and workload IAM permissions remain to be validated.
Terraform state is currently stored locally and excluded from Git.
