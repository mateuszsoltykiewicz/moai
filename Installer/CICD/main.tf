resource "helm_release" "cicd" {
  for_each = { for app in local.cicd_configs : app.name => app if app.enabled }

  name       = "${var.environment}-cicd-${each.value.name}"
  repository = each.value.repository != null ? each.value.repository : null
  chart      = each.value.chart
  version    = each.value.version
  namespace  = each.value.namespace != null ? each.value.namespace : "cicd"

  dynamic "values" {
    for_each = try([each.value.values_file], [])
    content {
      content = file(values.value)
    }
  }

  dynamic "set" {
    for_each = each.value.variables != null ? [for k, v in each.value.variables : { name = k, value = v }] : []
    content {
      name  = set.value.name
      value = tostring(set.value.value)
    }
  }

  timeout          = 600
  atomic           = true
  cleanup_on_fail  = true
}
