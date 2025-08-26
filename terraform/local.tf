locals {
  project_name = "car-api"
  environment  = "dev"
  region       = "us-east-1"

  ecr_repos = [
    local.project_name,
    format("%s-mkdocs", local.project_name)
  ]

  route53_zone_id = "Z01369533JWLF8Z0FCZQF"

  tags = {
    Project     = local.project_name
    Environment = local.environment
    Terraform   = "true"
  }
}
