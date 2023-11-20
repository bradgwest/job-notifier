"""Job Notifier"""

import argparse
import json
import logging
import os
import re
from typing import Any, Callable, Dict, List, Mapping, Tuple, Type, cast

import requests

from src.job import Job
from src.notifier.local import LocalNotifier, LocalNotifierConfig
from src.notifier.notifier import Notifier, NotifierConfig
from src.org import Org
from src.parser import parser
from src.storage.local import LocalStorage, LocalStorageConfig
from src.storage.storage import Storage, StorageConfig

_logger = logging.getLogger(__name__)

ConfigType = Type[NotifierConfig] | Type[StorageConfig]
BackendType = Type[Storage] | Type[Notifier]
Config = StorageConfig | NotifierConfig
Backend = Storage | Notifier
PageReader = Callable[[Org], str]
OrgMap = Dict[str, Org]

ORGANIZATIONS = {
    "airbnb": Org(
        "airbnb",
        "https://careers.airbnb.com/wp-admin/admin-ajax.php?"
        "action=fetch_greenhouse_jobs&which-board=airbnb&strip-empty=true",
        parser.AirbnbParser,
    ),
    "airtable": Org(
        "airtable", "https://boards.greenhouse.io/airtable", parser.AirtableParser
    ),
    "cloudflare": Org(
        "cloudflare",
        "https://boards-api.greenhouse.io/v1/boards/cloudflare/offices/",
        parser.CloudflareParser,
    ),
    "mongodb": Org(
        "mongodb",
        "https://www.mongodb.com/company/careers/teams/engineering",
        parser.MongoDBParser,
    ),
    "pintrest": Org(
        "pintrest", "https://www.pinterestcareers.com/en/jobs/", parser.PintrestParser
    ),
    "square": Org(
        "square",
        "https://careers.smartrecruiters.com/Square?remoteLocation=true",
        parser.SquareParser,
    ),
    "stripe": Org(
        "stripe",
        "https://stripe.com/jobs/search?remote_locations=North+America--US+Remote",
        parser.StripeParser,
    ),
    "zscaler": Org(
        "zscaler", "https://www.zscaler.com/careers#positions", parser.ZscalerParser
    ),
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


def reader(org: Org) -> str:
    r = requests.get(org.job_url)
    r.raise_for_status()
    _logger.debug(f"Read {len(r.content)} bytes from {org.name}")
    return r.content.decode(r.encoding or "utf-8")


class Runner:
    JOB_MATCHER = re.compile(r"engineer", re.IGNORECASE)

    def __init__(
        self,
        storage: Storage,
        notifier: Notifier,
        reader: PageReader,
        orgs: OrgMap,
    ) -> None:
        self.storage = storage
        self.notifier = notifier
        self.reader = reader
        self.orgs: OrgMap = orgs
        self.jobs: Dict[Org, List[Job]] = {}

    def _update(self, org: Org) -> None:
        parser = org.parser()
        content = self.reader(org)
        jobs = parser.parse(content)
        _logger.debug(f"Found {len(jobs)} jobs for {org.name}: {json.dumps(jobs)}")
        if not jobs:
            raise RuntimeError(f"No jobs found for {org.name}")
        self.storage.write(org.name, jobs)

    def update_storage(self) -> None:
        for org in self.orgs.values():
            self._update(org)

    def _match(self, job: Job) -> bool:
        return self.JOB_MATCHER.search(job.title) is not None

    def _diff(self, org: Org) -> List[Job]:
        page_count = 0
        jobs: List[List[Job]] = []
        for page in self.storage.read(org.name):
            jobs.append(page)
            page_count += 1
            if page_count == 2:
                break

        if page_count <= 0:
            raise RuntimeError(f"Storage for {org.name} is empty")
        elif page_count == 1:
            new_jobs = jobs[0]
        else:
            new_jobs = set(jobs[1]) - set(jobs[0])

        return [job for job in new_jobs if self._match(job)]

    def diff(self):
        jobs: Dict[Org, List[Job]] = {}
        for org in self.orgs.values():
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

    runner = Runner(storage, notifier, reader, ORGANIZATIONS)
    runner.run()
