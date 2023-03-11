data "tls_certificate" "demo_arm64" {
  url = aws_eks_cluster.demo_arm64.identity[0].oidc[0].issuer
}

resource "aws_iam_openid_connect_provider" "demo_arm64" {
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = [data.tls_certificate.demo_arm64.certificates[0].sha1_fingerprint]
  url             = aws_eks_cluster.demo_arm64.identity[0].oidc[0].issuer
}

data "tls_certificate" "demo_amd64" {
  url = aws_eks_cluster.demo_amd64.identity[0].oidc[0].issuer
}

resource "aws_iam_openid_connect_provider" "demo_amd64" {
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = [data.tls_certificate.demo_amd64.certificates[0].sha1_fingerprint]
  url             = aws_eks_cluster.demo_amd64.identity[0].oidc[0].issuer
}
