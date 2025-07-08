variable "environment" {
  type = string
}

variable "installer_type" {
  type = string
}

variable "kubeconfig_path" {
  description = "Path to kubeconfig file for cluster access"
  type        = string
}