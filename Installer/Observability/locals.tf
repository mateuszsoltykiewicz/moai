locals {
  environment    = var.environment
  installer_type = "observability"
  name_prefix    = "${local.environment}-${local.installer_type}"
  # Load and parse the observability YAML config
  observability_configs = yamldecode(file(var.observability_config_path)).observability
}