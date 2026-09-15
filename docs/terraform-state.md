# Terraform remote state

Migration date: 2026-09-15

## Backend

- Bucket: devops-eks-lab-tfstate-703671937762-us-east-1.
- Region: us-east-1.
- Public access blocked.
- Encryption: AES256.
- Versioning enabled.
- Bucket policy denies insecure transport.
- Native S3 state locking enabled with use_lockfile = true.
- Terraform requirement: >= 1.10, < 2.0.

## State separation

- bootstrap/terraform.tfstate: state bucket and its configuration.
- ecr/terraform.tfstate: ECR repository and Azure Pipelines OIDC/IAM.
- dynamodb/terraform.tfstate: application tasks table.

## Migration validation

- Local backups were verified against the original states.
- All three states were migrated using terraform init -migrate-state.
- All three state objects were confirmed in S3.
- Subsequent plans returned No changes for all configurations.
- Concurrent lock contention was not explicitly tested.

## Usage

Authenticate with AWS before running Terraform.
On a new checkout, run terraform init in each required directory.
Use -lock-timeout=5m to wait for an existing state lock.

Developers require IAM permissions for the resources they manage,
the corresponding state objects and their lock files.
The ECR publishing role has not been granted state access.

State files, local backups and saved plans must remain outside Git.
The bootstrap configuration protects the bucket with prevent_destroy.
