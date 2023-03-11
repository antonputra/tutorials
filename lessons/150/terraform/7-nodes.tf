resource "aws_iam_role" "nodes" {
  name = "eks-node-group-nodes"

  assume_role_policy = jsonencode({
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = {
        Service = "ec2.amazonaws.com"
      }
    }]
    Version = "2012-10-17"
  })
}

resource "aws_iam_role_policy_attachment" "nodes_amazon_eks_worker_node_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
  role       = aws_iam_role.nodes.name
}

resource "aws_iam_role_policy_attachment" "nodes_amazon_eks_cni_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
  role       = aws_iam_role.nodes.name
}

resource "aws_iam_role_policy_attachment" "nodes_amazon_ec2_container_registry_read_only" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
  role       = aws_iam_role.nodes.name
}

# Optional: only if you want to "SSH" to your EKS nodes.
resource "aws_iam_role_policy_attachment" "amazon_ssm_managed_instance_core" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
  role       = aws_iam_role.nodes.name
}

resource "aws_eks_node_group" "demo_arm64_private_nodes" {
  cluster_name    = aws_eks_cluster.demo_arm64.name
  node_group_name = "private-nodes"
  node_role_arn   = aws_iam_role.nodes.arn

  # Single subnet to avoid data transfer charges while testing.
  subnet_ids = [
    aws_subnet.private_us_east_1a.id
  ]

  capacity_type  = "ON_DEMAND"
  ami_type       = "AL2_ARM_64"
  instance_types = ["m6g.xlarge"]

  scaling_config {
    desired_size = 2
    max_size     = 6
    min_size     = 0
  }

  update_config {
    max_unavailable = 1
  }

  labels = {
    role = "general"
  }

  launch_template {
    name    = aws_launch_template.demo_arm64_eks_private_nodes.name
    version = aws_launch_template.demo_arm64_eks_private_nodes.latest_version
  }

  depends_on = [
    aws_iam_role_policy_attachment.nodes_amazon_eks_worker_node_policy,
    aws_iam_role_policy_attachment.nodes_amazon_eks_cni_policy,
    aws_iam_role_policy_attachment.nodes_amazon_ec2_container_registry_read_only,
  ]
}

resource "aws_launch_template" "demo_arm64_eks_private_nodes" {
  name = "demo-arm64-eks-private-nodes"

  tag_specifications {
    resource_type = "instance"

    tags = {
      "ec2-instance-type" = "m6g.xlarge"
    }
  }
}

resource "aws_eks_node_group" "demo_amd64_private_nodes" {
  cluster_name    = aws_eks_cluster.demo_amd64.name
  node_group_name = "private-nodes"
  node_role_arn   = aws_iam_role.nodes.arn

  # Single subnet to avoid data transfer charges while testing.
  subnet_ids = [
    aws_subnet.private_us_east_1a.id
  ]

  capacity_type  = "ON_DEMAND"
  ami_type       = "AL2_x86_64"
  instance_types = ["m6a.xlarge"]

  scaling_config {
    desired_size = 2
    max_size     = 6
    min_size     = 0
  }

  update_config {
    max_unavailable = 1
  }

  labels = {
    role = "general"
  }

  launch_template {
    name    = aws_launch_template.demo_amd64_eks_private_nodes.name
    version = aws_launch_template.demo_amd64_eks_private_nodes.latest_version
  }

  depends_on = [
    aws_iam_role_policy_attachment.nodes_amazon_eks_worker_node_policy,
    aws_iam_role_policy_attachment.nodes_amazon_eks_cni_policy,
    aws_iam_role_policy_attachment.nodes_amazon_ec2_container_registry_read_only,
  ]
}

resource "aws_launch_template" "demo_amd64_eks_private_nodes" {
  name = "demo-amd64-eks-private-nodes"

  tag_specifications {
    resource_type = "instance"

    tags = {
      "ec2-instance-type" = "m6a.xlarge"
    }
  }
}
