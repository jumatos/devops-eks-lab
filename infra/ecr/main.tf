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

resource "aws_ecr_repository" "api" {
  name                 = "devops-eks-lab-api"
  image_tag_mutability = "IMMUTABLE"
  force_delete         = false

  encryption_configuration {
    encryption_type = "AES256"
  }

  image_scanning_configuration {
    scan_on_push = true
  }
}

output "repository_url" {
  description = "URL del repositorio ECR para publicar imágenes."
  value       = aws_ecr_repository.api.repository_url
}

output "repository_arn" {
  description = "ARN del repositorio ECR para configurar permisos."
  value       = aws_ecr_repository.api.arn
}
