resource "helm_release" "cicd" {

  for_each = locals.enabled_cicd

  name             = each.key
  repository       = each.value.repo
  chart            = each.value.chart
  version          = each.value.version
  namespace        = each.value.ns
  create_namespace = true
  wait             = true

  values = [
    file("${path.module}/../../Configuration/cicd/${var.environment}/${each.key}/values.yaml")
  ]
}