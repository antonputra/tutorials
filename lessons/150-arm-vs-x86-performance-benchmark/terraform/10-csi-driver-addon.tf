resource "aws_eks_addon" "demo_arm64_csi_driver" {
  cluster_name             = aws_eks_cluster.demo_arm64.name
  addon_name               = "aws-ebs-csi-driver"
  addon_version            = "v1.15.0-eksbuild.1"
  service_account_role_arn = aws_iam_role.demo_arm64_eks_ebs_csi_driver.arn
}

resource "aws_eks_addon" "demo_amd64_csi_driver" {
  cluster_name             = aws_eks_cluster.demo_amd64.name
  addon_name               = "aws-ebs-csi-driver"
  addon_version            = "v1.15.0-eksbuild.1"
  service_account_role_arn = aws_iam_role.demo_amd64_eks_ebs_csi_driver.arn
}
