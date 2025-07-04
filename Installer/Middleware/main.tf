###############################
# Generic Secret Creation (extend as needed)
###############################
# Add here more resources for other middleware if you want to manage secrets for them

###############################
# Helm Releases for Middleware
###############################
resource "helm_release" "middleware" {
  for_each = local.enabled_middleware

  name             = each.key
  repository       = each.value.repo
  chart            = each.value.chart
  version          = each.value.version
  namespace        = each.value.ns
  create_namespace = true
  wait             = true

  values = [
    file("${path.module}/../../Configuration/middleware/${var.environment}/${each.key}/values.yaml")
  ]
}