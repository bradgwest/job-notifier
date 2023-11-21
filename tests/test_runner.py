from typing import List, NamedTuple, Optional, cast

import pytest

from src.job import Job
from src.notifier.notifier import Notifier
from src.parser import parser
from src.runner import PARSERS, Runner, config_from_env
from src.storage.storage import Storage


class ConfigTest(NamedTuple):
    path: str
    optional_var: Optional[str] = "test"
    env_var_prefix: str = "TESTER_BACKEND_"


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


def test_config_from_env_creates_config(monkeypatch: pytest.MonkeyPatch):
    test_path = "/test/path"
    test_optional_var = "updated_test_var"
    monkeypatch.setenv(ConfigTest._field_defaults["env_var_prefix"] + "PATH", test_path)
    monkeypatch.setenv(
        ConfigTest._field_defaults["env_var_prefix"] + "OPTIONAL_VAR",
        test_optional_var,
    )
    config = cast(ConfigTest, config_from_env(ConfigTest))
    assert config.path == test_path
    assert config.optional_var == test_optional_var


def test_config_from_env_raises_on_missing_env_var(monkeypatch: pytest.MonkeyPatch):
    with pytest.raises(RuntimeError):
        config_from_env(ConfigTest)


def test_runner(storage: Storage, notifier: Notifier, page_reader: parser.PageReader):
    runner = Runner(storage, notifier, page_reader, PARSERS)
    runner.run()
    assert len(runner.notifier.notifications) == len(PARSERS)  # type: ignore


def test_diff_raises_with_no_storage(
    storage: Storage, notifier: Notifier, page_reader: parser.PageReader
):
    runner = Runner(storage, notifier, page_reader, {"org": parser.Parser})
    with pytest.raises(RuntimeError):
        runner.diff()


def test_diff_returns_only_new_jobs(
    storage: Storage,
    notifier: Notifier,
    page_reader: parser.PageReader,
    listings: List[List[Job]],
):
    runner = Runner(storage, notifier, page_reader, {"org": parser.Parser})
    storage.write("org", listings[0])
    storage.write("org", listings[1])
    new_jobs = runner.diff()

    assert new_jobs == {
        "org": [Job("Mechanical Engineer", "https://mechanical-engineers.com/jobs")]
    }


def test_diff_returns_all_jobs_when_no_previous_jobs(
    storage: Storage,
    notifier: Notifier,
    page_reader: parser.PageReader,
    listings: List[List[Job]],
):
    runner = Runner(storage, notifier, page_reader, {"org": parser.Parser})
    storage.write("org", listings[0])
    new_jobs = runner.diff()

    assert new_jobs == {"org": listings[0]}
