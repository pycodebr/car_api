output "db_instance_endpoint" {
  description = "The endpoint of the RDS instance"
  value       = module.db.db_instance_endpoint 
}

output "db_instance_master_user_secret_arn" {
  description = "The ARN of the secret for the RDS instance master user"
  value       = module.db.db_instance_master_user_secret_arn
}

