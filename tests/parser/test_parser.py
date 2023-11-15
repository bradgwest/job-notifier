from typing import List

from bs4 import BeautifulSoup

from src.job import Job
from src.parser.parser import Parser


class TestParser(Parser):
    def _parse(self, soup: BeautifulSoup) -> List[Job]:
        return [
            Job(title=job.text.strip(), url=job["href"]) for job in soup.find_all("job")
        ]


def test_parser():
    content = """/
<html>
    <body>
        <job href="https://company_1.com/jobs/1">Engineer of Chairs</job>
        <job href="https://company_1.com/jobs/2">Cake Manufacturing Engineer</job>
    </body>
</html>
""".strip()

    parser = TestParser()
    jobs = parser.parse(content)
    assert len(jobs) == 2
    assert jobs[0] == Job(
        title="Engineer of Chairs", url="https://company_1.com/jobs/1"
    )
    assert jobs[1] == Job(
        title="Cake Manufacturing Engineer", url="https://company_1.com/jobs/2"
    )
