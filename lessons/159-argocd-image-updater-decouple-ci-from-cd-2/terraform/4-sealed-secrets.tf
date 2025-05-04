resource "helm_release" "sealed_secrets" {
  name = "sealed-secrets"

  repository       = "https://charts.bitnami.com/bitnami"
  chart            = "sealed-secrets"
  namespace        = "kube-system"
  create_namespace = true
  version          = "1.2.11"
}
