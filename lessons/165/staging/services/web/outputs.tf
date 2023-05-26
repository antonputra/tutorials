output "public_ip" {
  value       = aws_instance.example.public_ip
  description = "Public IP address of the web server."
}
