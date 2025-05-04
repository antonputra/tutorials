output "address" {
  value       = aws_db_instance.mydb.address
  description = "Database endpoint for establishing a connection to the database."
}

output "port" {
  value       = aws_db_instance.mydb.port
  description = "Database port for establishing a connection to the database."
}
