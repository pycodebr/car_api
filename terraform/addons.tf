module "eks_blueprints_addons" {
  source  = "aws-ia/eks-blueprints-addons/aws"
  version = "~> 1.0"

  cluster_name      = module.eks.cluster_name
  cluster_endpoint  = module.eks.cluster_endpoint
  cluster_version   = module.eks.cluster_version
  oidc_provider_arn = module.eks.oidc_provider_arn

  observability_tag = null

  enable_aws_load_balancer_controller = true
  enable_metrics_server               = true
  enable_external_dns                 = true
  enable_external_secrets             = true
  external_dns_route53_zone_arns = [
    format("arn:aws:route53:::hostedzone/%s", local.route53_zone_id)
  ]
  external_dns = {
    values = [
      <<-EOT
        provider: aws
        policy: sync
      EOT
    ]
  }

  tags = local.tags
}