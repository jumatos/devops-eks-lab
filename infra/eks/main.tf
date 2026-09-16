terraform {
  required_version = ">= 1.10, < 2.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 6.0"
    }
  }
}

provider "aws" {
  region              = "us-east-1"
  allowed_account_ids = ["703671937762"]

  default_tags {
    tags = {
      Project     = "devops-eks-lab"
      Environment = "lab"
      ManagedBy   = "Terraform"
    }
  }
}

variable "admin_public_cidr" {
  description = "Public IPv4 address allowed to reach the EKS API, with /32."
  type        = string

  validation {
    condition = (
      can(cidrnetmask(var.admin_public_cidr)) &&
      endswith(var.admin_public_cidr, "/32")
    )
    error_message = "Use a valid IPv4 address followed by /32."
  }
}

data "terraform_remote_state" "network" {
  backend = "s3"

  config = {
    bucket              = "devops-eks-lab-tfstate-703671937762-us-east-1"
    key                 = "network/terraform.tfstate"
    region              = "us-east-1"
    encrypt             = true
    allowed_account_ids = ["703671937762"]
  }
}

data "aws_iam_role" "lab_sso_admin" {
  name = "AWSReservedSSO_AdministratorAccess_139e5283d5f4ccc6"
}

resource "aws_iam_role" "cluster" {
  name = "devops-eks-lab-cluster"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "eks.amazonaws.com"
      }
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "cluster" {
  role       = aws_iam_role.cluster.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
}

resource "aws_eks_cluster" "lab" {
  name     = "devops-eks-lab"
  version  = "1.36"
  role_arn = aws_iam_role.cluster.arn

  bootstrap_self_managed_addons = false

  access_config {
    authentication_mode                         = "API"
    bootstrap_cluster_creator_admin_permissions = false
  }

  upgrade_policy {
    support_type = "STANDARD"
  }

  vpc_config {
    subnet_ids = data.terraform_remote_state.network.outputs.private_subnet_ids

    endpoint_private_access = true
    endpoint_public_access  = true
    public_access_cidrs     = [var.admin_public_cidr]
  }

  depends_on = [
    aws_iam_role_policy_attachment.cluster,
  ]
}

resource "aws_eks_access_entry" "lab_admin" {
  cluster_name  = aws_eks_cluster.lab.name
  principal_arn = data.aws_iam_role.lab_sso_admin.arn
  type          = "STANDARD"
}

resource "aws_eks_access_policy_association" "lab_admin" {
  cluster_name  = aws_eks_cluster.lab.name
  principal_arn = aws_eks_access_entry.lab_admin.principal_arn
  policy_arn    = "arn:aws:eks::aws:cluster-access-policy/AmazonEKSClusterAdminPolicy"

  access_scope {
    type = "cluster"
  }
}

output "cluster_name" {
  description = "EKS cluster name."
  value       = aws_eks_cluster.lab.name
}

output "cluster_endpoint" {
  description = "EKS Kubernetes API endpoint."
  value       = aws_eks_cluster.lab.endpoint
}

output "cluster_security_group_id" {
  description = "Security group created by EKS for the cluster."
  value       = aws_eks_cluster.lab.vpc_config[0].cluster_security_group_id
}
