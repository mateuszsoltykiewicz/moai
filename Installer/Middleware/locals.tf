locals {
  environment    = var.environment
  installer_type = "middleware"
  name_prefix    = "${local.environment}-${local.installer_type}"

  # Load and parse the middleware YAML config
  middleware_configs = yamldecode(file(var.middleware_config_path)).middleware
}
