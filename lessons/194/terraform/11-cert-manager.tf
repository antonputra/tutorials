resource "helm_release" "cert_manager" {
  name = "cert-manager"

  repository       = "https://charts.jetstack.io"
  chart            = "cert-manager"
  namespace        = "cert-manager"
  create_namespace = true
  version          = "v1.14.4"

  set {
    name  = "installCRDs"
    value = "true"
  }

  # Optional: Used for the DNS-01 challenge.
  set {
    name  = "serviceAccount.name"
    value = "cert-manager"
  }

  # Optional: Used for the DNS-01 challenge.
  set {
    name  = "serviceAccount.annotations.eks\\.amazonaws\\.com/role-arn"
    value = aws_iam_role.dns_manager.arn
  }

  depends_on = [aws_eks_node_group.general]
}
