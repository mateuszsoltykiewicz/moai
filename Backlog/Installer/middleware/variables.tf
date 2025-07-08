variable "environment" {
  type    = string
  default = "dev"
}

variable "kubeconfig_path" {
  type = string
  default = "~/.kube/config"
}

variable "role_arn" {
  type = string
}