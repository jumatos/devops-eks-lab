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

variable "enable_nat_gateway" {
  description = "Enable paid internet egress for private subnets."
  type        = bool
  default     = false
}

locals {
  zones = {
    a = {
      az           = "us-east-1a"
      public_cidr  = "10.20.0.0/24"
      private_cidr = "10.20.16.0/20"
    }
    b = {
      az           = "us-east-1b"
      public_cidr  = "10.20.1.0/24"
      private_cidr = "10.20.32.0/20"
    }
  }
}

resource "aws_vpc" "lab" {
  cidr_block           = "10.20.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "devops-eks-lab"
  }
}

resource "aws_internet_gateway" "lab" {
  vpc_id = aws_vpc.lab.id

  tags = {
    Name = "devops-eks-lab-igw"
  }
}

resource "aws_subnet" "public" {
  for_each = local.zones

  vpc_id                  = aws_vpc.lab.id
  availability_zone       = each.value.az
  cidr_block              = each.value.public_cidr
  map_public_ip_on_launch = false

  tags = {
    Name                     = "devops-eks-lab-public-${each.key}"
    "kubernetes.io/role/elb" = "1"
  }
}

resource "aws_subnet" "private" {
  for_each = local.zones

  vpc_id                  = aws_vpc.lab.id
  availability_zone       = each.value.az
  cidr_block              = each.value.private_cidr
  map_public_ip_on_launch = false

  tags = {
    Name                              = "devops-eks-lab-private-${each.key}"
    "kubernetes.io/role/internal-elb" = "1"
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.lab.id

  tags = {
    Name = "devops-eks-lab-public"
  }
}

resource "aws_route" "public_internet" {
  route_table_id         = aws_route_table.public.id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = aws_internet_gateway.lab.id
}

resource "aws_route_table_association" "public" {
  for_each = local.zones

  subnet_id      = aws_subnet.public[each.key].id
  route_table_id = aws_route_table.public.id
}

resource "aws_route_table" "private" {
  for_each = local.zones

  vpc_id = aws_vpc.lab.id

  tags = {
    Name = "devops-eks-lab-private-${each.key}"
  }
}

resource "aws_route_table_association" "private" {
  for_each = local.zones

  subnet_id      = aws_subnet.private[each.key].id
  route_table_id = aws_route_table.private[each.key].id
}

resource "aws_eip" "nat" {
  count = var.enable_nat_gateway ? 1 : 0

  domain = "vpc"

  tags = {
    Name = "devops-eks-lab-nat"
  }
}

resource "aws_nat_gateway" "lab" {
  count = var.enable_nat_gateway ? 1 : 0

  allocation_id = aws_eip.nat[0].id
  subnet_id     = aws_subnet.public["a"].id

  depends_on = [aws_internet_gateway.lab]

  tags = {
    Name = "devops-eks-lab-nat"
  }
}

resource "aws_route" "private_internet" {
  for_each = var.enable_nat_gateway ? local.zones : {}

  route_table_id         = aws_route_table.private[each.key].id
  destination_cidr_block = "0.0.0.0/0"
  nat_gateway_id         = aws_nat_gateway.lab[0].id
}

output "vpc_id" {
  value = aws_vpc.lab.id
}

output "public_subnet_ids" {
  value = [for key in sort(keys(local.zones)) : aws_subnet.public[key].id]
}

output "private_subnet_ids" {
  value = [for key in sort(keys(local.zones)) : aws_subnet.private[key].id]
}

output "nat_enabled" {
  value = var.enable_nat_gateway
}
