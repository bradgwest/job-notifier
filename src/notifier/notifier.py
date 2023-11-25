from typing import NamedTuple, Type

from src.job import Job, JobMap

NotifierConfig = Type[NamedTuple]


class Notifier:
    def __init__(self, config: NotifierConfig) -> None:
        self.config = config

    def _notify(self, org: str, job: Job) -> None:
        raise NotImplementedError()

    def notify(self, new_jobs: JobMap) -> None:
        for org, jobs in new_jobs.items():
            for job in jobs:
                self._notify(org, job)
