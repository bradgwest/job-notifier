from typing import List, NamedTuple

import requests
from bs4 import BeautifulSoup


class Job(NamedTuple):
    title: str
    url: str


class Parser:
    def parse(self, content: str) -> List[Job]:
        soup = BeautifulSoup(content, "lxml")
        return self._parse(soup)

    def _parse(self, soup: BeautifulSoup) -> List[Job]:
        raise NotImplementedError


def read(url: str) -> str:
    r = requests.get(url)
    r.raise_for_status()
    return r.content.decode(r.encoding or "utf-8")
