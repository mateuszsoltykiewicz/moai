resource "helm_release" "apps" {
  for_each = { for app in local.app_configs : app.name => app if app.enabled }

  name       = "${var.environment}-applications-${each.value.name}"
  repository = each.value.repository != null ? each.value.repository : null
  chart      = each.value.chart
  version    = each.value.version
  namespace  = each.value.namespace != null ? each.value.namespace : "default"

  # Optional: Load values file if provided
  dynamic "values" {
    for_each = try([each.value.values_file], [])
    content {
      content = file(values.value)
    }
  }

  # Pass additional variables as set blocks (including image digests)
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
