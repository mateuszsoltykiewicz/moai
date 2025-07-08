variable "environment" {
  description = "Deployment environment (e.g., dev, prod)"
  type        = string
}

variable "apps_config_path" {
  description = "Path to the apps.yaml configuration file"
  type        = string
}

variable "kubeconfig_path" {
  description = "Path to kubeconfig file for cluster access"
  type        = string
}
