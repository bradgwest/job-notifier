from typing import List, cast

import pytest

from src.job import Job
from src.notifier.notifier import Notifier
from src.org import Org
from src.parser.parser import Parser
from src.runner import ORGANIZATIONS, PageReader, Runner, config_from_env
from src.storage.storage import Storage
from tests.notifier.test_notifier import NotifierTest, NotifierTestConfig
from tests.storage.test_storage import StorageTest, StorageTestConfig


@pytest.fixture
def listings() -> List[List[Job]]:
    return [
        [
            Job("Aircraft Engineer", "https://aircraft-engineers.com/jobs"),
            Job("GPS Engineer", "https://gps-engineers.com/jobs"),
        ],
        [
            Job("Aircraft Engineer", "https://aircraft-engineers.com/jobs"),
            Job("Mechanical Engineer", "https://mechanical-engineers.com/jobs"),
        ],
    ]


@pytest.fixture
def org_map() -> dict[str, Org]:
    return {"org": Org("org", "url", Parser)}


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


def test_diff_raises_with_no_storage(
    storage: Storage,
    notifier: Notifier,
    page_reader: PageReader,
    org_map: dict[str, Org],
):
    runner = Runner(storage, notifier, page_reader, org_map)
    with pytest.raises(RuntimeError):
        runner.diff()


def test_diff_returns_only_new_jobs(
    storage: Storage,
    notifier: Notifier,
    page_reader: PageReader,
    listings: List[List[Job]],
    org_map: dict[str, Org],
):
    runner = Runner(storage, notifier, page_reader, org_map)
    storage.write("org", listings[0])
    storage.write("org", listings[1])
    new_jobs = runner.diff()

    assert new_jobs == {
        org_map["org"]: [
            Job("Mechanical Engineer", "https://mechanical-engineers.com/jobs")
        ]
    }


def test_diff_returns_all_jobs_when_no_previous_jobs(
    storage: Storage,
    notifier: Notifier,
    page_reader: PageReader,
    listings: List[List[Job]],
    org_map: dict[str, Org],
):
    org_map = {"org": Org("org", "url", Parser)}

    runner = Runner(storage, notifier, page_reader, org_map)
    storage.write("org", listings[0])
    new_jobs = runner.diff()

    assert new_jobs == {org_map["org"]: listings[0]}
