import io
from typing import List, NamedTuple, Optional

from src.job import Job
from src.storage.storage import Storage


class StorageTestConfig(NamedTuple):
    path: str
    optional_var: Optional[str] = "test"
    env_var_prefix: str = "TESTER_BACKEND_"


class StorageTest(Storage):
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

    def __init__(self, config: StorageTestConfig):
        self.config = config
        self.buffers: List[io.StringIO] = []

    def _read(self, org: str):
        for page in self.buffers:
            yield io.StringIO(page.getvalue())

    def _write(self, buff: io.StringIO, org: str):
        self.buffers.append(io.StringIO(buff.getvalue()))


def test_storage():
    storage = StorageTest(StorageTestConfig(path="/test/path"))
    org = "org"

    for page in storage.LISTINGS:
        storage.write(org, page)

    pages = list(storage.read(org))
    assert pages == StorageTest.LISTINGS
