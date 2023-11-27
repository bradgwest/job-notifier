import io
import json
from typing import Generator, List, NamedTuple, Type

from job_notifier.job import Job

StorageConfig = Type[NamedTuple]


class Storage:
    def __init__(self, config: StorageConfig) -> None:
        self.config = config

    def read(self, org: str) -> Generator[List[Job], None, None]:
        """Generate job listings from storage.

        Each list yielded is a different snapshot of the job listing, with
        the most recent first."""
        for buff in self._read(org):
            yield [Job(**d) for d in json.load(buff)]

    def write(self, org: str, jobs: List[Job]) -> None:
        buff = io.StringIO()
        json.dump([job.to_dict() for job in jobs], buff)
        self._write(buff, org)
        buff.close()

    def _read(self, org: str) -> Generator[io.StringIO, None, None]:
        raise NotImplementedError

    def _write(self, buff: io.StringIO, org: str) -> None:
        raise NotImplementedError
