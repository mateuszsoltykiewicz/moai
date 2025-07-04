data "template_file" "pg_init_script" {
  count    = contains(keys(local.middleware_with_secrets), "postgresql") ? 1 : 0
  template = file("${path.module}/init.sql.tmpl")
  vars = {
    users = [
      for u in local.pg_users : {
        name     = u.name
        password = random_password.pg_users[u.name].result
        database = u.database
      }
    ]
  }
}