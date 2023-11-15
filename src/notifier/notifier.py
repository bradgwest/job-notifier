from typing import Dict, List, NamedTuple, Type

from src.job import Job
from src.org import Org

NotifierConfig = Type[NamedTuple]


class Notifier:
    def __init__(self, config: NotifierConfig) -> None:
        self.config = config

    def _notify(self, org: Org, job: Job) -> None:
        raise NotImplementedError()

    def notify(self, new_jobs: Dict[Org, List[Job]]) -> None:
        for org, jobs in new_jobs.items():
            for job in jobs:
                self._notify(org, job)
