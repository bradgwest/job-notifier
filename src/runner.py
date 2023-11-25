"""Job Notifier"""

import argparse
import json
import logging
import os
import re
from collections import defaultdict
from typing import Any, Dict, Mapping, Tuple, Type, cast

import requests

from src.job import Job, JobMap
from src.notifier.local import LocalNotifier, LocalNotifierConfig
from src.notifier.notifier import Notifier, NotifierConfig
from src.parser import parser
from src.storage.local import LocalStorage, LocalStorageConfig
from src.storage.storage import Storage, StorageConfig

_logger = logging.getLogger(__name__)

ConfigType = Type[NotifierConfig] | Type[StorageConfig]
BackendType = Type[Storage] | Type[Notifier]
Config = StorageConfig | NotifierConfig
Backend = Storage | Notifier
ParserMap = Mapping[str, Type[parser.Parser]]

PARSERS = {
    "airbnb": parser.AirbnbParser,
    "airtable": parser.AirtableParser,
    "cloudflare": parser.CloudflareParser,
    "mongodb": parser.MongoDBParser,
    "netflix": parser.NetflixParser,
    "pintrest": parser.PintrestParser,
    "square": parser.SquareParser,
    "stripe": parser.StripeParser,
    "zscaler": parser.ZscalerParser,
}
STORAGE_BACKENDS: Mapping[str, Tuple[Type[Storage], ConfigType]] = {
    "LocalStorage": (LocalStorage, LocalStorageConfig),
}
NOTIFIER_BACKENDS: Mapping[str, Tuple[Type[Notifier], ConfigType]] = {
    "LocalNotifier": (LocalNotifier, LocalNotifierConfig),
}


def _log_level(val: str) -> int:
    try:
        return int(val)
    except ValueError:
        return getattr(logging, val.upper())


def config_from_env(cls: Config) -> Config:
    prefix = cls._field_defaults.get("env_var_prefix")
    if prefix is not None:
        kwargs: Dict[str, str] = {
            name[len(prefix) :].lower(): os.environ[name]
            for name in os.environ
            if name.startswith(prefix)
        }
    else:
        kwargs: Dict[str, str] = {}

    try:
        return cls(**kwargs)  # type: ignore
    except TypeError as e:
        raise RuntimeError(f"Could not create {cls.__name__} from environment") from e


def parse_backend(
    val: str,
    allowed_values: Mapping[str, Tuple[Type[Storage] | Type[Notifier], ConfigType]],
) -> Tuple[Type[Any], ConfigType]:
    try:
        return allowed_values[val]
    except KeyError:
        raise argparse.ArgumentTypeError(f"Unsupported backend: {val}")


def setup_backend(backend_type: BackendType, config: Config) -> Backend:
    cfg = config_from_env(config)
    return backend_type(cfg)


def reader(org: str, url: str) -> str:
    """Read a url, returning the content."""
    r = requests.get(url)
    r.raise_for_status()
    return r.content.decode(r.encoding or "utf-8")


class Runner:
    JOB_MATCHER = re.compile(r"engineer", re.IGNORECASE)

    def __init__(
        self,
        storage: Storage,
        notifier: Notifier,
        reader: parser.PageReader,
        parsers: ParserMap,
    ) -> None:
        self.storage = storage
        self.notifier = notifier
        self.parsers: ParserMap = parsers
        self.reader = reader
        self.jobs: JobMap = defaultdict(list)

    def _fetch(self) -> JobMap:
        """Fetch current job listings from all parsers."""
        jobs: JobMap = {}
        for org, parser_type in self.parsers.items():
            _logger.info(f"Fetching jobs for {org}")
            parser = parser_type()
            listings = parser.parse(self.reader)
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


# todo: add config for storage and notifier
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--log-level", type=_log_level, default="WARNING")
    parser.add_argument(
        "--storage-backend",
        type=lambda x: parse_backend(x, STORAGE_BACKENDS),
        default="LocalStorage",
    )
    parser.add_argument(
        "--notifier-backend",
        type=lambda x: parse_backend(x, NOTIFIER_BACKENDS),
        default="LocalNotifier",
    )
    args = parser.parse_args()

    logging.basicConfig()
    _logger.setLevel(args.log_level)

    storage = cast(Storage, setup_backend(*args.storage_backend))
    notifier = cast(Notifier, setup_backend(*args.notifier_backend))

    runner = Runner(storage, notifier, reader, PARSERS)
    runner.run()
