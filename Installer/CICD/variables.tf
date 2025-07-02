variable "environment" {
  description = "Deployment environment (e.g., dev, prod)"
  type        = string
}

variable "installer_type" {
  description = "Installer type (cicd)"
  type        = string
}

variable "cicd_config_path" {
  description = "Path to the cicd.yaml configuration file"
  type        = string
}

variable "kubeconfig_path" {
  description = "Path to kubeconfig file for cluster access"
  type        = string
}
