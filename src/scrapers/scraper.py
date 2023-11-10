from typing import List, NamedTuple, Optional

import requests


class Job(NamedTuple):
    title: str


class JobScraper:
    def __init__(self, url, parser) -> None:
        self.url = url
        self.parser = parser
        self.jobs: Optional[List[Job]] = None

    def read(self) -> bytes:
        """Read html from the job postings url"""
        r = requests.get(self.url)
        r.raise_for_status()
        return r.content

    def parse(self) -> None:
        """Parse jobs from html"""
        html = self.read()
        self.jobs = self.parser.parse(html)
