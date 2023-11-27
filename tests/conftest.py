import io
import os
from collections import defaultdict
from typing import Callable, Dict, List, NamedTuple, Optional

import pytest

from job_notifier.job import Job, JobMap
from job_notifier.notifier.notifier import Notifier
from job_notifier.storage.storage import Storage

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
LISTINGS_DIR = os.path.join(DATA_DIR, "listings")


class NotifierTestConfig(NamedTuple):
    pass


class NotifierTest(Notifier):
    def __init__(self, config: NotifierTestConfig):
        self.notifications: Dict[str, List[Job]] = defaultdict(list)

    def notify(self, new_jobs: JobMap) -> None:
        for org, jobs in new_jobs.items():
            for job in jobs:
                self.notifications[org].append(job)


class StorageTestConfig(NamedTuple):
    path: str
    optional_var: Optional[str] = "test"


class StorageTest(Storage):
    LISTINGS: List[List[Job]] = [
        [
            Job("Aircraft Engineer", "https://aircraft-engineers.com/jobs"),
            Job("GPS Engineer", "https://gps-engineers.com/jobs"),
        ],
        [
            Job("Aircraft Engineer", "https://aircraft-engineers.com/jobs"),
            Job("Mechanical Engineer", "https://mechanical-engineers.com/jobs"),
        ],
    ]

    def __init__(self, config: StorageTestConfig):
        self.config = config
        self.buffers: Dict[str, List[io.StringIO]] = defaultdict(list)

    def _read(self, org: str):
        for page in reversed(self.buffers.get(org, [])):
            yield io.StringIO(page.getvalue())

    def _write(self, buff: io.StringIO, org: str):
        self.buffers[org].append(io.StringIO(buff.getvalue()))


@pytest.fixture
def page_reader() -> Callable[[str, str], str]:
    def _reader(org: str, url: str) -> str:
        html_path = os.path.join(LISTINGS_DIR, f"{org}.txt")
        with open(html_path) as f:
            return f.read()

    return _reader


@pytest.fixture
def notifier() -> Notifier:
    return NotifierTest(NotifierTestConfig())


@pytest.fixture
def storage() -> Storage:
    return StorageTest(StorageTestConfig(path="/test/path"))
