import io
import os
from typing import Generator, NamedTuple

from job_notifier.storage.storage import Storage


class LocalStorageConfig(NamedTuple):
    path: str


class LocalStorage(Storage):
    def __init__(self, config: LocalStorageConfig):
        self.config = config

    def filepath(self, org: str) -> str:
        return os.path.join(self.config.path, f"{org}.json")

    def _read(self, org: str) -> Generator[io.StringIO, None, None]:
        fp = self.filepath(org)

        if not os.path.exists(fp):
            return

        with open(self.filepath(org)) as f:
            yield io.StringIO(f.read())

    def _write(self, buff: io.StringIO, org: str) -> None:
        fp = os.path.join(self.config.path, f"{org}.json")
        with open(fp, "w") as f:
            f.write(buff.getvalue())
