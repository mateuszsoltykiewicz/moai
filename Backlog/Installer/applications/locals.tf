locals {

  environment    = var.environment
  installer_type = "applications"
  name_prefix    = "${local.environment}-${local.installer_type}"

  # Load and parse the applications YAML config
  app_configs = yamldecode(file(var.apps_config_path)).apps
}