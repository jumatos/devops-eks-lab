data "aws_iam_role" "lab_sso_admin" {
  name = "AWSReservedSSO_AdministratorAccess_139e5283d5f4ccc6"
}

resource "aws_iam_role" "local_api" {
  name                 = "devops-eks-lab-local-api"
  description          = "Temporary DynamoDB access for local Minikube validation."
  max_session_duration = 3600

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        AWS = data.aws_iam_role.lab_sso_admin.arn
      }
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy" "local_api" {
  name = "task-table-access"
  role = aws_iam_role.local_api.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid    = "TaskTableAccess"
      Effect = "Allow"
      Action = [
        "dynamodb:GetItem",
        "dynamodb:PutItem",
        "dynamodb:UpdateItem",
        "dynamodb:DeleteItem",
        "dynamodb:Scan"
      ]
      Resource = aws_dynamodb_table.tasks.arn
    }]
  })
}

output "local_api_role_arn" {
  description = "Role for temporary local API validation credentials."
  value       = aws_iam_role.local_api.arn
}
