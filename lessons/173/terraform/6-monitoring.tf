data "kubectl_path_documents" "prometheus_operator" {
  pattern = "../monitoring/prometheus-operator/*.yaml"
}

resource "kubectl_manifest" "prometheus_operator" {
  for_each  = toset(data.kubectl_path_documents.prometheus_operator.documents)
  yaml_body = each.value

  depends_on = [helm_release.prometheus_operator_crds]
}

data "kubectl_path_documents" "prometheus" {
  pattern = "../monitoring/prometheus/*.yaml"
}

resource "kubectl_manifest" "prometheus" {
  for_each  = toset(data.kubectl_path_documents.prometheus.documents)
  yaml_body = each.value

  depends_on = [helm_release.prometheus_operator_crds]
}

data "kubectl_path_documents" "grafana_dashboards" {
  pattern = "../monitoring/grafana/dashboards/*.yaml"
}

resource "kubectl_manifest" "grafana_dashboards" {
  for_each  = toset(data.kubectl_path_documents.grafana_dashboards.documents)
  yaml_body = each.value

  depends_on = [helm_release.prometheus_operator_crds]
}

data "kubectl_path_documents" "grafana" {
  pattern = "../monitoring/grafana/*.yaml"
}

resource "kubectl_manifest" "grafana" {
  for_each  = toset(data.kubectl_path_documents.grafana.documents)
  yaml_body = each.value

  depends_on = [kubectl_manifest.grafana_dashboards]
}
