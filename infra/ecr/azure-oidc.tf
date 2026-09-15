locals {
  azure_oidc_host = "vstoken.dev.azure.com/85050c8b-0849-4cec-b426-48087a2c09ac"
  azure_oidc_aud  = "api://AzureADTokenExchange"
  azure_oidc_sub  = "sc://clavoops/devops-eks-lab/aws-ecr-publisher"
}

resource "aws_iam_openid_connect_provider" "azure" {
  url = "https://${local.azure_oidc_host}"

  client_id_list = [
    local.azure_oidc_aud,
  ]
}

resource "aws_iam_role" "azure_ecr_publisher" {
  name                 = "devops-eks-lab-azure-ecr-publisher"
  description          = "Publish lab API images from Azure Pipelines using OIDC."
  max_session_duration = 3600

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Federated = aws_iam_openid_connect_provider.azure.arn
        }
        Action = "sts:AssumeRoleWithWebIdentity"
        Condition = {
          StringEquals = {
            "${local.azure_oidc_host}:aud" = local.azure_oidc_aud
            "${local.azure_oidc_host}:sub" = local.azure_oidc_sub
          }
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "azure_ecr_publish" {
  name = "publish-lab-api"
  role = aws_iam_role.azure_ecr_publisher.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "AuthenticateToECR"
        Effect   = "Allow"
        Action   = "ecr:GetAuthorizationToken"
        Resource = "*"
      },
      {
        Sid    = "PublishToLabRepository"
        Effect = "Allow"
        Action = [
          "ecr:BatchCheckLayerAvailability",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload",
          "ecr:PutImage",
          "ecr:BatchGetImage",
          "ecr:DescribeImages",
        ]
        Resource = aws_ecr_repository.api.arn
      }
    ]
  })
}

output "azure_ecr_publisher_role_arn" {
  description = "Role used by the Azure DevOps service connection."
  value       = aws_iam_role.azure_ecr_publisher.arn
}
