resource "helm_release" "postgresql" {
  name = "postgresql"

  repository       = "https://charts.bitnami.com/bitnami"
  chart            = "postgresql"
  namespace        = "db"
  version          = "15.5.23"
  create_namespace = true

  values = [file("values/postgresql.yaml")]
}
