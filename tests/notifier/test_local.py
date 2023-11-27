import io

from job_notifier.job import Job
from job_notifier.notifier.local import LocalNotifier, LocalNotifierConfig


def test_local_notifier():
    new_jobs = {
        "company_1": [
            Job("Engineer of Chairs", "https://company_1.com/jobs/1"),
            Job("Cake Manufacturing Engineer", "https://company_1.com/jobs/2"),
        ],
        "company_2": [
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
