# Terraform Import Existing Resources AWS

### Initialize Terraform
```bash
$ terraform init
```

### Add VPC Resource and Run Terraform Plan
```bash
$ terraform plan
```

### Import AWS VPC using vpc id
```bash
$ terraform import aws_vpc.main vpc-<id>
```

### Add Subnets to Terraform

### Import Subnets using ids
```bash
$ terraform import aws_subnet.public subnet-<id>
$ terraform import aws_subnet.private subnet-<id>
```

### Add IGW to Terraform

### Import IGW using id
```bash
$ terraform import aws_internet_gateway.igw igw-<id>
```

### Add EIP to Terraform

### Import EIP using Public IP
```bash
$ terraform import aws_eip.nat_eip <ip-address>
```

### Add NAT Gateway to Terraform

### Import NAT Gateway using id
```bash
$ terraform import aws_nat_gateway.nat nat-<id>
```

### Add Routes and Route Associating to Terraform

### Import to Terraform State
```bash
$ terraform import aws_route_table.public rtb-<id>
$ terraform import aws_route_table.private rtb-<id>
$ terraform import aws_route_table_association.public subnet-<id>/rtb-<id>
$ terraform import aws_route_table_association.private subnet-<id>/rtb-<id>
```

### Add Security Group and EC2 to Terraform

### Import to Terraform State
```bash
$ terraform import aws_security_group.nginx sg-<id>
$ terraform import aws_instance.nginx i-<id>
```

### Add Route53 Hosted Zone and A Record to Terraform

### Import to Terraform State
```bash
$ terraform import aws_route53_zone.devops <id>
$ terraform import aws_route53_record.nginx <id>_api.devopsbyexample.io_A
```
