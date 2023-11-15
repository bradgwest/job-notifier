from typing import List

from bs4 import BeautifulSoup

from src.job import Job


class Parser:
    def parse(self, content: str) -> List[Job]:
        soup = BeautifulSoup(content, "lxml")
        return self._parse(soup)

    def _parse(self, soup: BeautifulSoup) -> List[Job]:
        raise NotImplementedError
