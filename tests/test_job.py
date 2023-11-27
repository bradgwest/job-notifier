from job_notifier.job import Job


def test_job():
    s = '{"title": "Aircraft Engineer", "url": "https://company_1.com/jobs/1"}'
    j = Job("Aircraft Engineer", "https://company_1.com/jobs/1")

    assert Job.from_json(s) == j
    assert j.to_json() == s
