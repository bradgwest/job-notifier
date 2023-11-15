"""Job Notifier"""

import argparse
import os
import re
from typing import Any, Dict, List, Mapping, NamedTuple, Optional, Tuple, Type

from src.job import Job
from src.notifier.local import LocalNotifier, LocalNotifierConfig
from src.notifier.notifier import Notifier
from src.org import Org
from src.parser.stripe import StripeParser
from src.storage.local import LocalStorage, LocalStorageConfig
from src.storage.storage import Storage

Config = Type[NamedTuple]

ORGANIZATIONS = [
    Org(
        "stripe",
        "https://stripe.com/jobs/search?remote_locations=North+America--US+Remote",
        StripeParser,
    ),
]
STORAGE_BACKENDS: Mapping[str | None, Tuple[Type[Storage], Type[Config]]] = {
    None: (LocalStorage, LocalStorageConfig),
    "LocalStorage": (LocalStorage, LocalStorageConfig),
}
NOTIFIER_BACKENDS: Mapping[str | None, Tuple[Type[Notifier], Type[Config]]] = {
    None: (LocalNotifier, LocalNotifierConfig),
    "LocalNotifier": (LocalNotifier, LocalNotifierConfig),
}


def config_from_env(cls: Config) -> NamedTuple:
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
        str | None, Tuple[Type[Storage] | Type[Notifier], Type[Config]]
    ],
) -> Tuple[Type[Any], Type[Config]]:
    if val in allowed_values:
        return allowed_values[val]

    raise argparse.ArgumentTypeError(f"Unsupported backend: {val}")


class Runner:
    JOB_MATCHER = re.compile(r"engineer", re.IGNORECASE)

    def __init__(self, storage: Storage, orgs: List[Org]) -> None:
        self.storage: Storage = storage
        self.orgs: List[Org] = orgs
        self.jobs: Dict[Org, List[Job]] = {}

    def _update(self, org: Org) -> None:
        parser = org.parser()
        jobs = parser.parse(org.job_url)
        self.storage.write(org.name, jobs)

    def update_storage(self) -> None:
        for org in self.orgs:
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
        for org in self.orgs:
            jobs[org] = self._diff(org)
        return jobs


def main(storage: Storage, notifier: Notifier, organizations: List[Org]) -> None:
    runner = Runner(storage, organizations)
    new_jobs = runner.diff()

    notifier.notify(new_jobs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--storage-backend", type=lambda x: parse_backend(x, STORAGE_BACKENDS)
    )
    parser.add_argument(
        "--notifier-backend", type=lambda x: parse_backend(x, NOTIFIER_BACKENDS)
    )
    args = parser.parse_args()

    storage_type, storage_config = args.storage_backend()
    cfg = config_from_env(storage_config)
    storage = storage_type(cfg)

    notifier_type, notifier_config = args.notifier_backend()
    cfg = config_from_env(notifier_config)
    notifier = notifier_type(cfg)

    main(storage, notifier, ORGANIZATIONS)
