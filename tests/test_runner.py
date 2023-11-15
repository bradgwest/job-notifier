from typing import cast

import pytest

from src.runner import ORGANIZATIONS, config_from_env, main
from tests.notifier.test_notifier import TesterNotifier, TesterNotifierConfig
from tests.storage.test_storage import TesterStorage, TesterStorageConfig


def test_config_from_env_creates_config(monkeypatch: pytest.MonkeyPatch):
    test_path = "/test/path"
    test_optional_var = "updated_test_var"
    monkeypatch.setenv(
        TesterStorageConfig._field_defaults["env_var_prefix"] + "PATH", test_path
    )
    monkeypatch.setenv(
        TesterStorageConfig._field_defaults["env_var_prefix"] + "OPTIONAL_VAR",
        test_optional_var,
    )
    config = cast(TesterStorageConfig, config_from_env(TesterStorageConfig))
    assert config.path == test_path
    assert config.optional_var == test_optional_var


def test_config_from_env_raises_on_missing_env_var(monkeypatch: pytest.MonkeyPatch):
    with pytest.raises(RuntimeError):
        config_from_env(TesterStorageConfig)


def test_main():
    cfg = TesterStorageConfig(path="/test/path")
    storage = TesterStorage(cfg)
    notifier = TesterNotifier(TesterNotifierConfig())
    with pytest.raises(RuntimeError):
        main(storage, notifier, ORGANIZATIONS)
