import argparse
from typing import List, NamedTuple, Optional, Set

import pytest

from src.job import Job
from src.notifier.notifier import Notifier
from src.parser import parser
from src.runner import (
    NOTIFIER_BACKENDS,
    PARSERS,
    STORAGE_BACKENDS,
    Runner,
    add_args,
    setup_notifier_backend,
    setup_storage_backend,
)
from src.storage.storage import Storage


class ConfigTest(NamedTuple):
    path: str
    optional_var: Optional[str] = "test"


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


def test_setup_storage_backend_errors_on_missing_arg():
    parser = add_args(argparse.ArgumentParser())
    cmdline = ["--storage-backend", "LocalStorage"]
    with pytest.raises(ValueError):
        args = parser.parse_args(cmdline)
        setup_storage_backend(args)


def test_setup_storage_backend():
    tested_classes: Set[str] = set()
    backends = {
        "LocalStorage": ["--local-storage-path", "/tmp"],
    }
    for backend_type, backend_args in backends.items():
        parser = add_args(argparse.ArgumentParser())
        cmdline = ["--storage-backend", backend_type] + backend_args
        args = parser.parse_args(cmdline)
        backend = setup_storage_backend(args)
        tested_classes.add(str(backend.__class__.__name__))

    assert tested_classes == STORAGE_BACKENDS


def test_setup_notifier_backend_errors_on_missing_arg():
    parser = add_args(argparse.ArgumentParser())
    cmdline = ["--notifier-backend", "GithubStepSummaryNotifier"]
    with pytest.raises(ValueError):
        args = parser.parse_args(cmdline)
        setup_notifier_backend(args)


def test_setup_notifier_backend():
    tested_classes: Set[str] = set()
    backends = {
        "LocalNotifier": [],
        "GithubStepSummaryNotifier": ["--github-username", "test"],
    }
    for backend_type, backend_args in backends.items():
        parser = add_args(argparse.ArgumentParser())
        cmdline = ["--notifier-backend", backend_type] + backend_args
        args = parser.parse_args(cmdline)
        backend = setup_notifier_backend(args)
        tested_classes.add(str(backend.__class__.__name__))

    assert tested_classes == NOTIFIER_BACKENDS


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
