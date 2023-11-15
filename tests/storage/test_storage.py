import io
from typing import List, NamedTuple, Optional

from src.job import Job
from src.storage.storage import Storage


class TesterStorageConfig(NamedTuple):
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

    def __init__(self, config: TesterStorageConfig):
        self.config = config
        self.buffers: List[io.StringIO] = []

    def _read(self, org: str):
        for page in self.buffers:
            yield io.StringIO(page.getvalue())

    def _write(self, buff: io.StringIO, org: str):
        self.buffers.append(io.StringIO(buff.getvalue()))


def test_config_from_env():
    pass


def test_storage():
    storage = TesterStorage(TesterStorageConfig(path="/test/path"))
    org = "org"

    for page in storage.LISTINGS:
        buff = io.StringIO()
        storage.write(org, page, buff)

    pages = list(storage.read(org))
    assert pages == TesterStorage.LISTINGS
