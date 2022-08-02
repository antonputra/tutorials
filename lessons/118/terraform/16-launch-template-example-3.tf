resource "aws_launch_template" "my-app-example-3" {
  name                   = "my-app-example-3"
  image_id               = "ami-0d5482f3cb962780f"
  key_name               = "devops"
  vpc_security_group_ids = [aws_security_group.my-app-example-3.id]
}
