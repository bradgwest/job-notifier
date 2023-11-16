import sys
from typing import NamedTuple, TextIO

from src.job import Job
from src.notifier.notifier import Notifier
from src.org import Org


class LocalNotifierConfig(NamedTuple):
    pass


class Colors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


class LocalNotifier(Notifier):
    def __init__(self, _: LocalNotifierConfig, file: TextIO = sys.stdout) -> None:
        self.file = file

    def _notify(self, org: Org, job: Job) -> None:
        print(
            "New job:"
            f"{Colors.BOLD}{Colors.OKBLUE}{job.title}{Colors.ENDC}{Colors.ENDC}"
            " at "
            f"{Colors.OKCYAN}{org.name}{Colors.ENDC}",
            file=self.file,
        )
