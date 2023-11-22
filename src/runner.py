"""Job Notifier"""

import argparse
import json
import logging
import os
import re
from typing import Any, Dict, List, Mapping, Tuple, Type, cast

import requests

from src.job import Job
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
        self.jobs: Dict[str, List[Job]] = {}

    def update_storage(self) -> None:
        for org, parser_type in self.parsers.items():
            parser = parser_type()
            jobs = parser.parse(self.reader)
            _logger.debug(f"Found {len(jobs)} jobs for {org}: {json.dumps(jobs)}")
            if not jobs:
                raise RuntimeError(f"No jobs found for {org}")
            self.storage.write(org, jobs)

    def _match(self, job: Job) -> bool:
        return self.JOB_MATCHER.search(job.title) is not None

    def _diff(self, org: str) -> List[Job]:
        page_count = 0
        jobs: List[List[Job]] = []
        for page in self.storage.read(org):
            jobs.append(page)
            page_count += 1
            if page_count == 2:
                break

        if page_count <= 0:
            raise RuntimeError(f"Storage for {org} is empty")
        elif page_count == 1:
            new_jobs = jobs[0]
        else:
            new_jobs = set(jobs[0]) - set(jobs[1])

        return [job for job in new_jobs if self._match(job)]

    def diff(self):
        jobs: Dict[str, List[Job]] = {}
        for org in self.parsers.keys():
            jobs[org] = self._diff(org)
        return jobs

    def run(self) -> None:
        self.update_storage()
        new_jobs = self.diff()
        self.notifier.notify(new_jobs)


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
