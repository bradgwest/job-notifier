import sys
from typing import NamedTuple, TextIO

from job_notifier.job import Job, JobMap
from job_notifier.notifier.notifier import Notifier


class LocalNotifierConfig(NamedTuple):
    pass


class LocalNotifier(Notifier):
    BASE_COLOR = 91
    DISTINCT_COLORS = 6
    BOLD = "\033[1m"
    END_BOLD = "\033[22m"
    END_COLOR = "\033[0m"
    ITALIC = "\033[3m"
    END_ITALIC = "\033[23m"

    def __init__(self, _: LocalNotifierConfig, file: TextIO = sys.stdout) -> None:
        self.file = file
        self._org: str = ""
        self.seq = 0

    def _color(self, org: str) -> str:
        self.seq += int(org != self._org)
        self._org = org
        return str(self.BASE_COLOR + self.seq % self.DISTINCT_COLORS)

    def _notify(self, org: str, job: Job) -> None:
        color = f"\033[{self._color(org)}m"

        print(
            f"{color}{org}{self.END_COLOR}: "
            f"{self.BOLD}{job.title}{self.END_BOLD} - "
            f"{self.ITALIC}{job.url}{self.END_ITALIC}",
            file=self.file,
        )

    def notify(self, new_jobs: JobMap) -> None:
        for org, jobs in new_jobs.items():
            for job in jobs:
                self._notify(org, job)
