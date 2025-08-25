module "db" {
  source  = "terraform-aws-modules/rds/aws"
  version = "6.12.0"

  identifier = "car-api-db"

  engine            = "postgres"
  engine_version    = "17"
  instance_class    = "db.t4g.large"
  allocated_storage = 5

  db_name  = "car_api"
  username = "car_api"
  port     = "3306"

  family = "postgres17"

  vpc_security_group_ids = [
    "sg-0c4c8a7a6dc2b864c"
  ]

  tags = {
    Owner       = "pycodebr"
    Environment = "dev"
  }

  create_db_subnet_group = true
  subnet_ids             = module.vpc.private_subnets

  # Database Deletion Protection
  deletion_protection = true
}