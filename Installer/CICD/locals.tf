locals {
  environment = var.environment
  installer_type = var.installer_type

  # Naming prefix for all resources
  name_prefix = "${local.environment}-${local.installer_type}"

  # Common labels for tagging resources
  common_labels = {
    environment = local.environment
    installer   = local.installer_type
  }

  # Load and parse the cicd YAML config
  cicd_configs = yamldecode(file(var.cicd_config_path)).cicd
}
