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

data "kubectl_path_documents" "cadvisor" {
  pattern = "../monitoring/cadvisor/*.yaml"
}

resource "kubectl_manifest" "cadvisor" {
  for_each  = toset(data.kubectl_path_documents.cadvisor.documents)
  yaml_body = each.value

  depends_on = [helm_release.prometheus_operator_crds]
}

data "kubectl_path_documents" "kube_state_metrics" {
  pattern = "../monitoring/kube-state-metrics/*.yaml"
}

resource "kubectl_manifest" "kube_state_metrics" {
  for_each  = toset(data.kubectl_path_documents.kube_state_metrics.documents)
  yaml_body = each.value

  depends_on = [helm_release.prometheus_operator_crds]
}
