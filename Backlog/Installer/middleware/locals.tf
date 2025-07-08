locals {
  # Load middleware YAML config
  middleware_config = yamldecode(file("${path.module}/../../Configuration/installer/middleware/middleware.yaml"))["middleware"]

  # Only enabled middleware
  enabled_middleware = {
    for name, cfg in local.middleware_config : name => cfg if try(cfg.enable, false)
  }

  # Only enabled middleware with secrets
  middleware_with_secrets = {
    for name, cfg in local.enabled_middleware : name => cfg if try(cfg.secrets.enable, false)
  }
}