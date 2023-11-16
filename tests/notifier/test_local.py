import io

from src.job import Job
from src.notifier.local import LocalNotifier, LocalNotifierConfig
from src.org import Org
from src.parser.parser import Parser


def test_local_notifier():
    new_jobs = {
        Org("company_1", "https://company_1.com/jobs", Parser): [
            Job("Engineer of Chairs", "https://company_1.com/jobs/1"),
            Job("Cake Manufacturing Engineer", "https://company_1.com/jobs/2"),
        ],
        Org("company_2", "https://company_2.com/jobs", Parser): [
            Job("Widget Engineer 3", "https://company_2.com/jobs/1"),
            Job("People Engineer 4", "https://company_2.com/jobs/2"),
            Job("Hard Things Engineer 5", "https://company_2.com/jobs/3"),
        ],
    }

    buff = io.StringIO()
    notifier = LocalNotifier(LocalNotifierConfig(), buff)
    notifier.notify(new_jobs)

    buff.seek(0)
    lines = buff.readlines()

    assert len(lines) == 5
