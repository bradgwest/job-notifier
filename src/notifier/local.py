from typing import NamedTuple

from src.job import Job
from src.notifier.notifier import Notifier
from src.org import Org


class LocalNotifierConfig(NamedTuple):
    pass


class LocalNotifier(Notifier):
    def _notify(self, org: Org, job: Job) -> None:
        print(f"New job: {job.title} at {org.name}")
