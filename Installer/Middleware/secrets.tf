###############################
# Dynamic PostgreSQL Passwords
###############################
locals {
  pg_users = try(local.middleware_with_secrets["postgresql"]["users"], [])
}

resource "random_password" "pg_users" {
  for_each = { for u in local.pg_users : u.name => u }
  length   = 24
  special  = true
}

resource "kubernetes_secret" "pg_initdb" {
  count = contains(keys(local.middleware_with_secrets), "postgresql") ? 1 : 0

  metadata {
    name      = "postgresql-initdb-secrets"
    namespace = local.enabled_middleware["postgresql"].ns
  }
  type = "Opaque"
  data = {
    for u in local.pg_users :
    "${u.name}-password" => base64encode(random_password.pg_users[u.name].result)
  }
}

resource "kubernetes_secret" "pg_initdb_script" {
  count = contains(keys(local.middleware_with_secrets), "postgresql") ? 1 : 0

  metadata {
    name      = "postgresql-initdb-script"
    namespace = local.enabled_middleware["postgresql"].ns
  }
  type = "Opaque"
  data = {
    "init.sql" = base64encode(data.template_file.pg_init_script[0].rendered)
  }
}

resource "random_password" "redis" {
  length  = 24
  special = false
}

resource "kubernetes_secret" "redis" {
  count = try(local.enabled_middleware["redis"].secrets.enable, false) ? 1 : 0

  metadata {
    name      = "redis-secret"
    namespace = local.enabled_middleware["redis"].ns
  }
  type = "Opaque"
  data = {
    "redis-password" = base64encode(random_password.redis.result)
  }
}