import pytest

from app.config.settings import Settings


@pytest.mark.parametrize(
    "url, expected",
    [
        ("postgresql://u:p@localhost:5433/orion", "postgresql+psycopg2://u:p@localhost:5433/orion"),
        ("postgres://u:p@localhost/orion", "postgresql+psycopg2://u:p@localhost/orion"),
        ("postgresql+psycopg://u:p@localhost/orion", "postgresql+psycopg://u:p@localhost/orion"),
        ("sqlite:///./orion.db", "sqlite:///./orion.db"),
    ],
)
def test_database_url_pins_installed_postgres_driver(url, expected):
    assert Settings(DATABASE_URL=url).DATABASE_URL == expected
