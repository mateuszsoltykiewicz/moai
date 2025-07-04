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

provider "aws" {
  region = "eu-central-1"

  assume_role {
    role_arn     = var.role_arn
    session_name = "terraform-session"
  }
}