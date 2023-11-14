"""Job Notifier"""

import argparse
from typing import NamedTuple, Optional, Type

from src.parser.parser import Parser
from src.parser.stripe import StripeParser
from src.storage.local import LocalStorage
from src.storage.storage import Storage


class Org(NamedTuple):
    name: str
    job_url: str
    parser: Type[Parser]


ORGANIZATIONS = (
    Org(
        "stripe",
        "https://stripe.com/jobs/search?remote_locations=North+America--US+Remote",
        StripeParser,
    ),
)


def parse_storage_backend(val: Optional[str]) -> Type[Storage]:
    match val:
        case None:
            return LocalStorage
        case "LocalStorage":
            return LocalStorage
        case _:
            raise argparse.ArgumentTypeError(f"Unsupported storage backend: {val}")


def diff_org(store: Storage):
    pass


def main(storage: Storage) -> None:
    # cfg = config_from_env(config)

    for org in ORGANIZATIONS:
        diff_org(storage)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--storage-backend", type=parse_storage_backend)
    args = parser.parse_args()

    main(args.storage_backend)
