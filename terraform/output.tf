output "db_instance_address" {
  description = "The endpoint of the RDS instance"
  value       = module.db.db_instance_address
}

output "db_instance_master_user_secret" {
  description = "The ARN of the secret for the RDS instance master user"
  value       = split(":", module.db.db_instance_master_user_secret_arn)[length(split(":", module.db.db_instance_master_user_secret_arn)) - 1]
}

