from src.job import Job
from src.notifier.notifier import Notifier
from src.org import Org
from src.parser.parser import Parser


def test_notifier(notifier: Notifier):
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

    notifier.notify(new_jobs)
    assert len(notifier.notifications) == 2  # type: ignore
    assert len(notifier.notifications["company_1"]) == 2  # type: ignore
    assert len(notifier.notifications["company_2"]) == 3  # type: ignore
