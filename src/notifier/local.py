import sys
from typing import NamedTuple, TextIO

from src.job import Job
from src.notifier.notifier import Notifier
from src.org import Org


class LocalNotifierConfig(NamedTuple):
    pass


class Colors:
    # ANSI escape codes
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


class LocalNotifier(Notifier):
    def __init__(self, _: LocalNotifierConfig, file: TextIO = sys.stdout) -> None:
        self.file = file

    def _notify(self, org: Org, job: Job) -> None:
        print(
            f"{Colors.BOLD}{Colors.CYAN}{org.name}{Colors.ENDC}{Colors.ENDC}: "
            f"{Colors.BLUE}{job.title}{Colors.ENDC} - "
            f"{Colors.GREEN}{job.url}{Colors.ENDC}",
            file=self.file,
        )
