module "oidc_gitlab_com" {
  source  = "gitlab.com/gitlab-com/terraform-gitlab-aws-oidc/local"
  version = "~> 1.2.0" # Note: update this to reflect the current release...

  oidc_roles = {
    # Allow all branches of gitlab-com/gl-infra/project to obtain ReadOnlyAccess
    branch = {
      role_name   = "GitLabCIOIDC-Project-Branch"
      role_path   = "/ci/"
      match_field = "sub"
      match_value = ["project_path:mateusmuller2/fastapi-pycodebr:ref_type:branch:ref:*"]
      policy_arns = ["arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryFullAccess"]

      assume_role_principal_arns = []
    }
  }
}