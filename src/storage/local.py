from typing import List, NamedTuple

from src.job import Job
from src.storage.storage import Storage


class LocalConfig(NamedTuple):
    path: str


class LocalStorage(Storage):
    def read(self, company: str) -> List[Job]:
        return []

    def write(self, company: str, jobs: List[Job]) -> None:
        pass
