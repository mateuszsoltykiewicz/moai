locals {
  cicd_config = yamldecode(file("${path.module}/../../Configuration/installer/cicd/cicd.yaml"))["cicd"]

  enabled_cicd = {
    for name, cfg in local.cicd_config : name => cfg if try(cfg.enable, false)
  }
}