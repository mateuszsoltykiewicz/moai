variable "environment" {
  description = "Deployment environment (e.g., dev, prod)"
  type        = string
}

variable "middleware_config_path" {
  description = "Path to the middleware.yaml configuration file"
  type        = string
}

variable "kubeconfig_path" {
  description = "Path to kubeconfig file for cluster access"
  type        = string
}
