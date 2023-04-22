# variable "custom_ports" {
#   description = "Custom ports to open on the security group."
#   type        = map(any)

#   default = {
#     80   = ["0.0.0.0/0"]
#     8081 = ["10.0.0.0/16"]
#   }
# }

# resource "aws_security_group" "web" {
#   name   = "allow-web-access"
#   vpc_id = aws_vpc.main.id

#   ingress {
#     from_port   = 80
#     to_port     = 80
#     protocol    = "tcp"
#     cidr_blocks = ["0.0.0.0/0"]
#   }
# }
