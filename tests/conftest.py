import io
import os
from collections import defaultdict
from typing import Dict, List, NamedTuple, Optional

import pytest

from src.job import Job
from src.notifier.notifier import Notifier
from src.org import Org
from src.runner import PageReader
from src.storage.storage import Storage

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
LISTINGS_DIR = os.path.join(DATA_DIR, "listings")


class NotifierTestConfig(NamedTuple):
    pass


class NotifierTest(Notifier):
    def __init__(self, config: NotifierTestConfig):
        self.notifications: Dict[str, List[Job]] = defaultdict(list)

    def _notify(self, org: Org, job: Job) -> None:
        self.notifications[org.name].append(job)


class StorageTestConfig(NamedTuple):
    path: str
    optional_var: Optional[str] = "test"
    env_var_prefix: str = "TESTER_BACKEND_"


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
        self.buffers: List[io.StringIO] = []

    def _read(self, org: str):
        for page in self.buffers:
            yield io.StringIO(page.getvalue())

    def _write(self, buff: io.StringIO, org: str):
        self.buffers.append(io.StringIO(buff.getvalue()))


@pytest.fixture
def page_reader() -> PageReader:
    def _reader(org: Org) -> str:
        html_path = os.path.join(LISTINGS_DIR, f"{org.name}.txt")
        with open(html_path) as f:
            return f.read()

    return _reader


@pytest.fixture
def notifier() -> Notifier:
    return NotifierTest(NotifierTestConfig())


@pytest.fixture
def storage() -> Storage:
    return StorageTest(StorageTestConfig(path="/test/path"))
