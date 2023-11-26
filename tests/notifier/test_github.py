from src.job import Job
from src.notifier.github import (
    GithubStepSummaryNotifier,
    GithubStepSummaryNotifierConfig,
)


def test_summary():
    notifier = GithubStepSummaryNotifier(
        GithubStepSummaryNotifierConfig(github_username="test")
    )
    new_jobs = {
        "abc": [
            Job("Aircraft Engineer", "https://abc.com/jobs/123"),
            Job("Mechanical Engineer", "https://abc.com/jobs/456"),
        ],
        "xyz": [Job("GPS Engineer", "https://xyz.com/jobs/789")],
    }
    expected = """\
@test
## abc
* [Aircraft Engineer](https://abc.com/jobs/123)
* [Mechanical Engineer](https://abc.com/jobs/456)
## xyz
* [GPS Engineer](https://xyz.com/jobs/789)
"""
    actual = notifier.summarize(new_jobs, "test")
    assert actual == expected
