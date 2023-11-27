from typing import NamedTuple, Type

from job_notifier.job import JobMap

NotifierConfig = Type[NamedTuple]


class Notifier:
    def __init__(self, config: NamedTuple) -> None:
        self.config = config

    def notify(self, new_jobs: JobMap) -> None:
        raise NotImplementedError
