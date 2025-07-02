

locals {
  platform_configs = yamldecode(file("${path.module}/../../Configuration/Installer/Platform/platform.yaml")).platform
}

module "platform_modules" {
  for_each = { for mod in local.platform_configs : mod.name => mod if mod.enabled }
  source   = each.value.chart
  name     = each.value.name
  version  = each.value.version
  values   = fileexists(each.value.values_file) ? file(each.value.values_file) : null

  # Pass additional variables as Helm set values
  dynamic "set" {
    for_each = each.value.variables != null ? [for k, v in each.value.variables : {name = k, value = v}] : []
    content {
      name  = set.value.name
      value = tostring(set.value.value)
    }
  }
}
