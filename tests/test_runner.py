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


def test_diff(storage: Storage, notifier: Notifier, page_reader: parser.PageReader):
    current = {
        "xyz": [
            Job("Aircraft Engineer", "https://xyz.com/jobs/387"),
            Job("GPS Engineer", "https://xyz.com/jobs/123"),
        ],
        "abc": [
            Job("Mechanical Engineer", "https://abc.com/jobs/234"),
        ],
    }
    cached = {
        "xyz": [
            Job("Aircraft Engineer", "https://xyz.com/jobs/387"),
        ],
        "abc": [
            Job("Physical Engineer", "https://abc.com/jobs/123"),
            Job("Mechanical Engineer", "https://abc.com/jobs/234"),
        ],
    }
    runner = Runner(
        storage, notifier, page_reader, {"xyz": parser.Parser, "abc": parser.Parser}
    )
    new_jobs = runner.diff(current, cached)
    assert new_jobs == {
        "xyz": [Job("GPS Engineer", "https://xyz.com/jobs/123")],
        "abc": [],
    }


def test_run(storage: Storage, notifier: Notifier, page_reader: parser.PageReader):
    class XYZParser(parser.Parser):
        def parse(self, reader: parser.PageReader) -> List[Job]:
            return [
                Job("Aircraft Engineer", "https://xyz.com/jobs/387"),
                Job("GPS Engineer", "https://xyz.com/jobs/123"),
            ]

    class ABCParser(parser.Parser):
        def parse(self, reader: parser.PageReader) -> List[Job]:
            return [
                Job("Mechanical Engineer", "https://abc.com/jobs/234"),
            ]

    parsers = {"xyz": XYZParser, "abc": ABCParser}

    storage.write("xyz", [Job("Aircraft Engineer", "https://xyz.com/jobs/387")])
    storage.write("abc", [Job("Physical Engineer", "https://abc.com/jobs/123")])

    runner = Runner(storage, notifier, page_reader, parsers)
    runner.run()

    assert runner.notifier.notifications == {  # type: ignore
        "xyz": [Job("GPS Engineer", "https://xyz.com/jobs/123")],
        "abc": [Job("Mechanical Engineer", "https://abc.com/jobs/234")],
    }
