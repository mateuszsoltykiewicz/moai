terraform {
  required_providers {
    helm = {
      source  = "hashicorp/helm"
      version = ">=2.0.0"
    }
  }
  required_version = ">= 1.3.0"
}

provider "helm" {
  kubernetes {
    config_path = var.kubeconfig_path
  }
}