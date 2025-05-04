output "alb_dns_name" {
  value       = aws_lb.example.dns_name
  description = "DNS of the application load balancer"
}
