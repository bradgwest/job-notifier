"""Job Notifier"""

import argparse
import os
import re
from typing import Any, Callable, Dict, List, Mapping, Optional, Tuple, Type, cast

import requests

from src.job import Job
from src.notifier.local import LocalNotifier, LocalNotifierConfig
from src.notifier.notifier import Notifier, NotifierConfig
from src.org import Org
from src.parser.stripe import StripeParser
from src.storage.local import LocalStorage, LocalStorageConfig
from src.storage.storage import Storage, StorageConfig

ConfigType = Type[NotifierConfig] | Type[StorageConfig]
BackendType = Type[Storage] | Type[Notifier]
Config = StorageConfig | NotifierConfig
Backend = Storage | Notifier
PageReader = Callable[[Org], str]
OrgMap = Dict[str, Org]

ORGANIZATIONS = {
    "stripe": Org(
        "stripe",
        "https://stripe.com/jobs/search?remote_locations=North+America--US+Remote",
        StripeParser,
    ),
}
STORAGE_BACKENDS: Mapping[str | None, Tuple[Type[Storage], ConfigType]] = {
    None: (LocalStorage, LocalStorageConfig),
    "LocalStorage": (LocalStorage, LocalStorageConfig),
}
NOTIFIER_BACKENDS: Mapping[str | None, Tuple[Type[Notifier], ConfigType]] = {
    None: (LocalNotifier, LocalNotifierConfig),
    "LocalNotifier": (LocalNotifier, LocalNotifierConfig),
}


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
    val: Optional[str],
    allowed_values: Mapping[
        str | None, Tuple[Type[Storage] | Type[Notifier], ConfigType]
    ],
) -> Tuple[Type[Any], ConfigType]:
    try:
        return allowed_values[val]
    except KeyError:
        raise argparse.ArgumentTypeError(f"Unsupported backend: {val}")


def setup_backend(backend_type: BackendType, config: Config) -> Backend:
    cfg = config_from_env(config)
    return backend_type(cfg)


def page_reader(org: Org) -> str:
    r = requests.get(org.job_url)
    r.raise_for_status()
    return r.content.decode(r.encoding or "utf-8")


class Runner:
    JOB_MATCHER = re.compile(r"engineer", re.IGNORECASE)

    def __init__(
        self,
        storage: Storage,
        notifer: Notifier,
        reader: PageReader,
        orgs: OrgMap,
    ) -> None:
        self.storage = storage
        self.notifier = notifer
        self.reader = reader
        self.orgs: OrgMap = orgs
        self.jobs: Dict[Org, List[Job]] = {}

    def _update(self, org: Org) -> None:
        parser = org.parser()
        content = self.reader(org)
        jobs = parser.parse(content)
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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--storage-backend", type=lambda x: parse_backend(x, STORAGE_BACKENDS)
    )
    parser.add_argument(
        "--notifier-backend", type=lambda x: parse_backend(x, NOTIFIER_BACKENDS)
    )
    args = parser.parse_args()

    storage = cast(Storage, setup_backend(*args.storage_backend()))
    notifier = cast(Notifier, setup_backend(*args.notifier_backend()))

    runner = Runner(storage, notifier, page_reader, ORGANIZATIONS)
    runner.run()
