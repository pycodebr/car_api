module "ecr" {
  source  = "terraform-aws-modules/ecr/aws"
  version = "~> 2.4.0"

  for_each = toset(local.ecr_repos)

  create_lifecycle_policy = false

  repository_name         = each.value
  repository_force_delete = true

  tags = local.tags
}
