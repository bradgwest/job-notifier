import datetime
import io
import os
from typing import Generator, NamedTuple, Optional

from src.storage.storage import Storage


class LocalConfig(NamedTuple):
    path: str
    env_var_prefix: str = "LOCAL_STORAGE_"


class LocalStorage(Storage):
    def __init__(self, config: LocalConfig):
        self.config = config

    def directory(self, org: str) -> str:
        return os.path.join(self.config.path, org)

    def filepath(self, org: str, dt: Optional[datetime.datetime] = None) -> str:
        if dt is None:
            dt = datetime.datetime.now(tz=datetime.timezone.utc)

        directory = self.directory(org)
        ts = dt.strftime("%y%m%dT%H%M%S")
        return os.path.join(directory, f"{org}_{ts}.json")

    def _read(self, org: str) -> Generator[io.StringIO, None, None]:
        directory = self.directory(org)
        files = sorted(
            [file for file in os.listdir(directory) if file.endswith(".json")],
            key=lambda x: os.path.getmtime(os.path.join(self.directory(org), x)),
            reverse=True,
        )
        for file in files:
            with open(file) as f:
                yield io.StringIO(f.read())

    def _write(self, buff: io.StringIO, org: str) -> None:
        directory = self.directory(org)
        if not os.path.exists(directory):
            os.mkdir(directory)

        fp = self.filepath(org)
        with open(fp, "w") as f:
            f.write(buff.getvalue())

    def clean(self) -> None:
        """Remove all by the most recent two files for each org"""
        # todo
        pass
