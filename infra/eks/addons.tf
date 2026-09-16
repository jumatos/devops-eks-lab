resource "aws_iam_role" "vpc_cni" {
  name = "devops-eks-lab-vpc-cni"

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
          "aws:RequestTag/kubernetes-namespace"       = "kube-system"
          "aws:RequestTag/kubernetes-service-account" = "aws-node"
        }
      }
    }]
  })
}

resource "aws_iam_role_policy_attachment" "vpc_cni" {
  role       = aws_iam_role.vpc_cni.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
}

resource "aws_eks_addon" "pod_identity_agent" {
  cluster_name  = aws_eks_cluster.lab.name
  addon_name    = "eks-pod-identity-agent"
  addon_version = "v1.3.10-eksbuild.3"

  resolve_conflicts_on_update = "PRESERVE"
}

resource "aws_eks_addon" "vpc_cni" {
  cluster_name  = aws_eks_cluster.lab.name
  addon_name    = "vpc-cni"
  addon_version = "v1.22.4-eksbuild.3"

  resolve_conflicts_on_update = "PRESERVE"

  pod_identity_association {
    role_arn        = aws_iam_role.vpc_cni.arn
    service_account = "aws-node"
  }

  depends_on = [
    aws_iam_role_policy_attachment.vpc_cni,
    aws_eks_addon.pod_identity_agent,
  ]
}

resource "aws_eks_addon" "kube_proxy" {
  cluster_name  = aws_eks_cluster.lab.name
  addon_name    = "kube-proxy"
  addon_version = "v1.36.0-eksbuild.21"

  resolve_conflicts_on_update = "PRESERVE"
}

resource "aws_eks_addon" "coredns" {
  cluster_name  = aws_eks_cluster.lab.name
  addon_name    = "coredns"
  addon_version = "v1.14.3-eksbuild.16"

  resolve_conflicts_on_update = "PRESERVE"

  depends_on = [
    aws_eks_node_group.lab,
  ]
}