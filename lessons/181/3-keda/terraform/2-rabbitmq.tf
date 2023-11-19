# Install Manually
# helm repo add bitnami https://charts.bitnami.com/bitnami
# helm repo update
# helm install rabbitmq bitnami/rabbitmq --version 12.5.1 --namespace rabbitmq --create-namespace
resource "helm_release" "rabbitmq" {
  name = "rabbitmq"

  repository       = "https://charts.bitnami.com/bitnami"
  chart            = "rabbitmq"
  namespace        = "rabbitmq"
  create_namespace = true
  version          = "12.5.1"

  set {
    name  = "auth.username"
    value = "myapp"
  }

  set {
    name  = "auth.password"
    value = "devops123"
  }
}
