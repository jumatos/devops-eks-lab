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

resource "aws_dynamodb_table" "tasks" {
  name         = "devops-eks-lab-tasks"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "id"

  attribute {
    name = "id"
    type = "S"
  }
}

output "table_name" {
  description = "Value for the API DYNAMODB_TABLE_NAME environment variable."
  value       = aws_dynamodb_table.tasks.name
}

output "table_arn" {
  description = "Table ARN for the API IAM permissions."
  value       = aws_dynamodb_table.tasks.arn
}
