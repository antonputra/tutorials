# Instructions to create VPC

- Create VPC

```bash
aws ec2 create-vpc \
  --cidr-block 10.0.0.0/16 \
  --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=main}]'
```

- Create public subnet

```bash
aws ec2 create-subnet \
--vpc-id <your-vpc-id> \
--availability-zone us-east-1a \
--cidr-block 10.0.0.0/24 \
--tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=public}]'
```

- Create private subnet

```bash
aws ec2 create-subnet \
--vpc-id <your-vpc-id> \
--availability-zone us-east-1b \
--cidr-block 10.0.1.0/24 \
--tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=private}]'
```

- Allocate IP for NAT Gateway

```bash
aws ec2 allocate-address
```

- Create NAT Gateway

```bash
aws ec2 create-nat-gateway \
--subnet-id <your-subnet-id> \
--allocation-id <your-eipalloc-id> \
--tag-specifications 'ResourceType=natgateway,Tags=[{Key=Name,Value=my-nat-gateway}]'
```

- Create internet gateway

```bash
aws ec2 create-internet-gateway
```

- Cretae public route table

```bash
aws ec2 create-route-table \
--vpc-id <your-vpc-id> \
--tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=public-route}]'
```

- Attach internet gateway

```bash
aws ec2 attach-internet-gateway \
--internet-gateway-id <your-igw-id> \
--vpc-id vpc-0724881ef1256d0ee
```

- Create default route to Internet

```bash
aws ec2 create-route \
--route-table-id <your-rtb-id> \
--destination-cidr-block 0.0.0.0/0 \
--gateway-id <your-igw-id>
```

- Cretae private route table

```bash
aws ec2 create-route-table \
--vpc-id <your-vpc-id> \
--tag-specifications 'ResourceType=route-table,Tags=[{Key=Name,Value=private-route}]'
```

- Create default route to NAT gateway

```bash
aws ec2 create-route \
--route-table-id <your-rtb-id> \
--destination-cidr-block 0.0.0.0/0 \
--nat-gateway-id <your-nat-id>
```

- Change routing table for public subnet

```bash
aws ec2 associate-route-table \
--route-table-id <your-rtb-id> \
--subnet-id <your-subnet->
```

- - Change routing table for private subnet

```bash
aws ec2 associate-route-table \
--route-table-id <your-rtb-id> \
--subnet-id <your-subnet-id>
```

- Updaye public subnet to assign public IPs

```bash
aws ec2 modify-subnet-attribute \
--subnet-id <your-subnet-id> \
--map-public-ip-on-launch
```
