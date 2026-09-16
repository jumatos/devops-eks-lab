data "terraform_remote_state" "dynamodb" {
  backend = "s3"

  config = {
    bucket              = "devops-eks-lab-tfstate-703671937762-us-east-1"
    key                 = "dynamodb/terraform.tfstate"
    region              = "us-east-1"
    encrypt             = true
    allowed_account_ids = ["703671937762"]
  }
}

resource "aws_iam_role" "task_api" {
  name        = "devops-eks-lab-task-api"
  description = "DynamoDB access for the task API through EKS Pod Identity."

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Service = "pods.eks.amazonaws.com"
      }
      Action = [
        "sts:AssumeRole",
        "sts:TagSession",
      ]
      Condition = {
        StringEquals = {
          "aws:RequestTag/eks-cluster-name"           = aws_eks_cluster.lab.name
          "aws:RequestTag/kubernetes-namespace"       = "task-api"
          "aws:RequestTag/kubernetes-service-account" = "task-api"
        }
      }
    }]
  })
}

resource "aws_iam_role_policy" "task_api" {
  name = "task-table-access"
  role = aws_iam_role.task_api.id

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
        "dynamodb:Scan",
      ]
      Resource = data.terraform_remote_state.dynamodb.outputs.table_arn
    }]
  })
}

resource "aws_eks_pod_identity_association" "task_api" {
  cluster_name    = aws_eks_cluster.lab.name
  namespace       = "task-api"
  service_account = "task-api"
  role_arn        = aws_iam_role.task_api.arn

  depends_on = [
    aws_iam_role_policy.task_api,
    aws_eks_addon.pod_identity_agent,
  ]
}

output "task_api_role_arn" {
  description = "IAM role used by the task API through EKS Pod Identity."
  value       = aws_iam_role.task_api.arn
}