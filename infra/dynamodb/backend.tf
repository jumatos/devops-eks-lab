terraform {
  backend "s3" {
    bucket              = "devops-eks-lab-tfstate-703671937762-us-east-1"
    key                 = "dynamodb/terraform.tfstate"
    region              = "us-east-1"
    encrypt             = true
    use_lockfile        = true
    allowed_account_ids = ["703671937762"]
  }
}
