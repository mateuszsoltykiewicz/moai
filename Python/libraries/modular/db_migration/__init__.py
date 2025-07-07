# /Python/libraries/modular/db_migration/__init__.py
import alembic.config
import alembic.command

def run_migrations(alembic_cfg_path):
    alembic_cfg = alembic.config.Config(alembic_cfg_path)
    alembic.command.upgrade(alembic_cfg, "head")
