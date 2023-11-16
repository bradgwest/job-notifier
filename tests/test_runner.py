from typing import cast

import pytest

from src.notifier.notifier import Notifier
from src.runner import ORGANIZATIONS, PageReader, Runner, config_from_env
from src.storage.storage import Storage
from tests.notifier.test_notifier import NotifierTest, NotifierTestConfig
from tests.storage.test_storage import StorageTest, StorageTestConfig


@pytest.fixture
def storage() -> Storage:
    return StorageTest(StorageTestConfig(path="/test/path"))


@pytest.fixture
def notifier() -> Notifier:
    return NotifierTest(NotifierTestConfig())


def test_config_from_env_creates_config(monkeypatch: pytest.MonkeyPatch):
    test_path = "/test/path"
    test_optional_var = "updated_test_var"
    monkeypatch.setenv(
        StorageTestConfig._field_defaults["env_var_prefix"] + "PATH", test_path
    )
    monkeypatch.setenv(
        StorageTestConfig._field_defaults["env_var_prefix"] + "OPTIONAL_VAR",
        test_optional_var,
    )
    config = cast(StorageTestConfig, config_from_env(StorageTestConfig))
    assert config.path == test_path
    assert config.optional_var == test_optional_var


def test_config_from_env_raises_on_missing_env_var(monkeypatch: pytest.MonkeyPatch):
    with pytest.raises(RuntimeError):
        config_from_env(StorageTestConfig)


def test_runner(storage: Storage, notifier: Notifier, page_reader: PageReader):
    runner = Runner(storage, notifier, page_reader, ORGANIZATIONS)
    runner.run()
    assert len(runner.notifier.notifications) == 22  # type: ignore


def test_diff_raises_with_no_storage(page_reader: PageReader):
    pass
