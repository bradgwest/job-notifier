import os
from typing import List, NamedTuple, cast

from job_notifier.job import Job, JobMap
from job_notifier.notifier.notifier import Notifier


class GithubStepSummaryNotifierConfig(NamedTuple):
    github_username: str


class GithubStepSummaryNotifier(Notifier):
    def __init__(self, config: GithubStepSummaryNotifierConfig) -> None:
        super().__init__(config)

    @staticmethod
    def summarize(new_jobs: JobMap, username: str) -> str:
        def _org(org: str, jobs: List[Job]) -> str:
            return f"## {org}\n" + "\n".join(
                f"* [{job.title}]({job.url})"
                for job in sorted(jobs, key=lambda j: j.title)
            )

        return (
            f"@{username}\n"
            + "\n".join(_org(org, jobs) for org, jobs in new_jobs.items())
            + "\n"
        )

    def notify(self, new_jobs: JobMap) -> None:
        summary = self.summarize(
            new_jobs,
            cast(GithubStepSummaryNotifierConfig, self.config).github_username,
        )

        with open(os.environ["GITHUB_STEP_SUMMARY"], "w") as f:
            f.write(summary)
