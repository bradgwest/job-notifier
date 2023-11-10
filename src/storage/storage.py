import os
from typing import List, NamedTuple

from src.job import Job


# todo: test me
def config_from_env(cls) -> NamedTuple:
    match cls.__name__:
        case "LocalConfig":
            prefix = "LOCAL_STORAGE_"
        case _:
            raise ValueError(f"Unknown config class {cls.__name__}")

    kwargs = {
        name[len(prefix) :].lower(): os.environ[name]
        for name in os.environ
        if name.startswith(prefix)
    }

    try:
        return cls(**kwargs)
    except TypeError as e:
        raise RuntimeError(f"Could not create {cls.__name__} from environment") from e


class Storage:
    def __init__(self, config: NamedTuple):
        self.config = config

    def read(self, company: str) -> List[Job]:
        raise NotImplementedError

    def write(self, company: str, jobs: List[Job]) -> None:
        raise NotImplementedError
