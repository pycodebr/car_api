module "db" {
  source  = "terraform-aws-modules/rds/aws"
  version = "~> 6.12.0"

  identifier = format("%s-db", local.project_name)

  engine            = "postgres"
  engine_version    = "17"
  instance_class    = "db.t4g.large"
  allocated_storage = 5

  db_name  = local.project_name
  username = local.project_name
  port     = "3306"

  family = "postgres17"

  vpc_security_group_ids = [module.vpc.default_security_group_id]

  tags = local.tags

  create_db_subnet_group = true
  subnet_ids             = module.vpc.private_subnets
}