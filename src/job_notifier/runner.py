"""Job Notifier"""

import argparse
import json
import logging
import os
import re
from collections import defaultdict
from typing import Mapping, Type

from job_notifier.job import Job, JobMap
from job_notifier.notifier.github import (
    GithubStepSummaryNotifier,
    GithubStepSummaryNotifierConfig,
)
from job_notifier.notifier.local import LocalNotifier, LocalNotifierConfig
from job_notifier.notifier.notifier import Notifier, NotifierConfig
from job_notifier.parser import parser
from job_notifier.storage.local import LocalStorage, LocalStorageConfig
from job_notifier.storage.storage import Storage, StorageConfig

_logger = logging.getLogger(__name__)

ConfigType = Type[NotifierConfig] | Type[StorageConfig]
BackendType = Type[Storage] | Type[Notifier]
Config = StorageConfig | NotifierConfig
Backend = Storage | Notifier
ParserMap = Mapping[str, Type[parser.Parser]]

PARSERS = {
    "affirm": parser.AffirmParser,
    "airbnb": parser.AirbnbParser,
    "airtable": parser.AirtableParser,
    "cloudflare": parser.CloudflareParser,
    "mongodb": parser.MongoDBParser,
    "netflix": parser.NetflixParser,
    "nvidia": parser.NvidiaParser,
    "pintrest": parser.PintrestParser,
    "ramp": parser.RampParser,
    "reddit": parser.RedditParser,
    "square": parser.SquareParser,
    "stripe": parser.StripeParser,
    "vectara": parser.VectaraParser,
    "zillow": parser.ZillowParser,
    "zscaler": parser.ZscalerParser,
}
STORAGE_BACKENDS = frozenset(["LocalStorage"])
NOTIFIER_BACKENDS = frozenset(["LocalNotifier", "GithubStepSummaryNotifier"])


def _log_level(val: str) -> int:
    try:
        return int(val)
    except ValueError:
        return getattr(logging, val.upper())


def setup_storage_backend(args: argparse.Namespace) -> Storage:
    match args.storage_backend:
        case "LocalStorage":
            if args.local_storage_path is None:
                raise ValueError(
                    "LocalStorage backend requires setting --local-storage-path"
                )
            return LocalStorage(LocalStorageConfig(args.local_storage_path))
        case _:
            raise ValueError(f"Unsupported storage backend: {args.storage_backend}")


def setup_notifier_backend(args: argparse.Namespace) -> Notifier:
    match args.notifier_backend:
        case "LocalNotifier":
            return LocalNotifier(LocalNotifierConfig())
        case "GithubStepSummaryNotifier":
            if args.github_username is None:
                raise ValueError(
                    "GithubStepSummaryNotifier backend requires setting "
                    "--github-username"
                )
            return GithubStepSummaryNotifier(
                GithubStepSummaryNotifierConfig(args.github_username)
            )
        case _:
            raise ValueError(f"Unsupported notifier backend: {args.notifier_backend}")


class Runner:
    JOB_MATCHER = re.compile(r"engineer", re.IGNORECASE)

    def __init__(
        self,
        storage: Storage,
        notifier: Notifier,
        parsers: ParserMap,
    ) -> None:
        self.storage = storage
        self.notifier = notifier
        self.parsers: ParserMap = parsers
        self.jobs: JobMap = defaultdict(list)

    def _fetch(self) -> JobMap:
        """Fetch current job listings from all parsers."""
        jobs: JobMap = {}
        for org, parser_type in self.parsers.items():
            _logger.info(f"Fetching jobs for {org}")
            p = parser_type(getattr(parser_type, "reader", parser.reader))
            listings = p.parse()
            _logger.info(f"Found {len(listings)} jobs for {org}")
            _logger.debug(f"Jobs for {org}: {json.dumps(jobs)}")
            jobs[org] = listings
        return jobs

    def _read_cache(self) -> JobMap:
        """Read cached job listings from storage."""
        jobs: JobMap = {}

        for org in self.parsers.keys():
            try:
                page = next(self.storage.read(org))
            except StopIteration:
                _logger.info(f"Storage for {org} is empty")
                page = []

            jobs[org] = page

        return jobs

    def update_storage(self, jobs: JobMap) -> None:
        """Update storage with current job listings."""
        for org, listings in jobs.items():
            self.storage.write(org, listings)

    def _match(self, job: Job) -> bool:
        return self.JOB_MATCHER.search(job.title) is not None

    def diff(self, current: JobMap, cached: JobMap) -> JobMap:
        """Return new jobs that are not in cache."""
        jobs: JobMap = {}

        for org in self.parsers.keys():
            jobs[org] = [
                job for job in set(current[org]) - set(cached[org]) if self._match(job)
            ]

        return jobs

    def run(self) -> None:
        """Run the job notifier.

        This will fetch current job listings, compare them to the cached listings,
        and notify of any new jobs.
        """
        current = self._fetch()
        cached = self._read_cache()
        new = self.diff(current, cached)
        # Default to notifying first. On the off chance updating storage fails,
        # we'll get notified more than once. This is OK for now.
        self.notifier.notify(new)
        self.update_storage(current)


def add_args(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    parser.add_argument("--log-level", type=_log_level, default="WARNING")
    parser.add_argument(
        "--storage-backend",
        default="LocalStorage",
        choices=STORAGE_BACKENDS,
    )
    parser.add_argument(
        "--notifier-backend",
        default="LocalNotifier",
        choices=NOTIFIER_BACKENDS,
    )
    parser.add_argument(
        "--local-storage-path",
        help="Path to directory in which to store files when using the "
        "LocalStorage backend",
        default=os.getenv("NOTIFIER_LOCAL_STORAGE_PATH"),
    )
    parser.add_argument(
        "--github-username",
        help="Github username to notify when using the GithubStepSummaryNotifier "
        "backend",
        default=os.getenv("NOTIFIER_GITHUB_USERNAME"),
    )
    return parser


def main():
    parser = add_args(argparse.ArgumentParser(description=__doc__))
    args = parser.parse_args()

    logging.basicConfig()
    _logger.setLevel(args.log_level)

    storage = setup_storage_backend(args)
    notifier = setup_notifier_backend(args)

    runner = Runner(storage, notifier, PARSERS)
    runner.run()
