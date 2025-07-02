variable "environment" {
  description = "Deployment environment (e.g., dev, prod)"
  type        = string
}

variable "observability_config_path" {
  description = "Path to the observability.yaml configuration file"
  type        = string
}

variable "kubeconfig_path" {
  description = "Path to kubeconfig file for cluster access"
  type        = string
}
