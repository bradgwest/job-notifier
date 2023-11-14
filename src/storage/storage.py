import io
import json
import os
from typing import Dict, Generator, List, NamedTuple, Optional, Type

from src.job import Job


def config_from_env(cls: Type[NamedTuple]) -> NamedTuple:
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


class Storage:
    def read(self, org: str) -> Generator[List[Job], None, None]:
        """Generate job listings from storage.

        Each list yielded is a different snapshot of the job listing, with
        the most recent first."""
        for buff in self._read(org):
            yield [Job(**d) for d in json.load(buff)]

    def write(
        self, org: str, jobs: List[Job], buff: Optional[io.StringIO] = None
    ) -> None:
        if buff is None:
            buff = io.StringIO()
        json.dump([job.to_dict() for job in jobs], buff)
        self._write(buff, org)
        buff.close()

    def _read(self, org: str) -> Generator[io.StringIO, None, None]:
        raise NotImplementedError

    def _write(self, buff: io.StringIO, org: str) -> None:
        raise NotImplementedError

    def clean(self) -> None:
        """Clean up unnecessary storage"""
        raise NotImplementedError
