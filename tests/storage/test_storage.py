import io
from typing import NamedTuple, Optional, cast

import pytest

from src.job import Job
from src.storage.storage import Storage, config_from_env


class TesterConfig(NamedTuple):
    path: str
    optional_var: Optional[str] = "test"
    env_var_prefix: str = "TESTER_BACKEND_"


class TesterStorage(Storage):
    LISTINGS = [
        [
            Job("Aircraft Engineer", "https://aircraft-engineers.com/jobs"),
            Job("GPS Engineer", "https://gps-engineers.com/jobs"),
        ],
        [
            Job("Aircraft Engineer", "https://aircraft-engineers.com/jobs"),
            Job("Mechanical Engineer", "https://mechanical-engineers.com/jobs"),
        ],
    ]

    def __init__(self, config: Optional[NamedTuple] = None):
        self.buffers = []

    def _read(self, org):
        for page in self.buffers:
            yield io.StringIO(page.getvalue())

    def _write(self, buff, org):
        self.buffers.append(io.StringIO(buff.getvalue()))


def test_config_from_env():
    pass


def test_storage():
    store = TesterStorage()
    org = "org"

    for page in store.LISTINGS:
        buff = io.StringIO()
        store.write(org, page, buff)

    pages = list(store.read(org))
    assert pages == TesterStorage.LISTINGS


def test_config_from_env_creates_config(monkeypatch):
    test_path = "/test/path"
    test_optional_var = "updated_test_var"
    monkeypatch.setenv(
        TesterConfig._field_defaults["env_var_prefix"] + "PATH", test_path
    )
    monkeypatch.setenv(
        TesterConfig._field_defaults["env_var_prefix"] + "OPTIONAL_VAR",
        test_optional_var,
    )
    config = cast(TesterConfig, config_from_env(TesterConfig))
    assert config.path == test_path
    assert config.optional_var == test_optional_var


def test_config_from_env_raises_on_missing_env_var(monkeypatch):
    with pytest.raises(RuntimeError):
        config_from_env(TesterConfig)
