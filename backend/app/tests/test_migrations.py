from pathlib import Path

from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import create_engine, inspect

from app.config.settings import settings

ALEMBIC_DIR = Path(__file__).resolve().parents[2] / "alembic"


def _alembic_config() -> Config:
    # No ini file on purpose: env.py would call fileConfig() and disable the loggers other tests rely on.
    cfg = Config()
    cfg.set_main_option("script_location", str(ALEMBIC_DIR))
    return cfg


def test_single_alembic_head():
    heads = ScriptDirectory.from_config(_alembic_config()).get_heads()
    assert len(heads) == 1, f"multiple Alembic heads: {heads}"


def test_upgrade_head_on_fresh_sqlite(tmp_path, monkeypatch):
    url = f"sqlite:///{(tmp_path / 'fresh.db').as_posix()}"
    monkeypatch.setattr(settings, "DATABASE_URL", url)   # env.py reads the URL from settings
    cfg = _alembic_config()

    command.upgrade(cfg, "head")
    columns = {c["name"]: c for c in inspect(create_engine(url)).get_columns("events")}
    assert "sequence_index" in columns and columns["sequence_index"]["nullable"]

    command.downgrade(cfg, "-1")
    assert "sequence_index" not in {c["name"] for c in inspect(create_engine(url)).get_columns("events")}
