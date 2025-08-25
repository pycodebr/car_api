data "aws_route53_zone" "mateusmullerme" {
  name         = "mateusmuller.me."
  private_zone = false
}

module "records" {
  source  = "terraform-aws-modules/route53/aws//modules/records"
  version = "5.0.0"

  zone_name = data.aws_route53_zone.mateusmullerme.name

  records = [
    {
      name    = "rds-car-api"
      type    = "CNAME"
      records        = [module.db.db_instance_endpoint]
      ttl = 300
    },
  ]
}