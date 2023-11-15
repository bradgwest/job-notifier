from typing import NamedTuple, Type

from src.parser.parser import Parser


class Org(NamedTuple):
    name: str
    job_url: str
    parser: Type[Parser]
