resource "aws_iam_role" "eks" {
  name = "eks-cluster-${var.eks_cluster_name}"

  assume_role_policy = <<POLICY
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "eks.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
POLICY
}

resource "aws_iam_role_policy_attachment" "eks_amazon_eks_cluster_policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
  role       = aws_iam_role.eks.name
}

resource "aws_eks_cluster" "this" {
  name     = var.eks_cluster_name
  version  = "1.27"
  role_arn = aws_iam_role.eks.arn

  vpc_config {
    subnet_ids = concat(
      module.vpc.private_subnets,
      module.vpc.public_subnets
    )
  }

  depends_on = [aws_iam_role_policy_attachment.eks_amazon_eks_cluster_policy]
}
