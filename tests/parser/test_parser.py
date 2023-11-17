from typing import List, NamedTuple

from bs4 import BeautifulSoup

from src.job import Job
from src.parser import parser
from src.runner import ORGANIZATIONS, PageReader


class TestParser(parser.Parser):
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


def test_org_parsers(page_reader: PageReader):
    class Test(NamedTuple):
        parser: parser.Parser
        expected: List[Job]

    cases = {
        "airbnb": Test(
            parser.AirbnbParser(),
            [
                Job(
                    "Senior Software Engineer, Trust Platform",
                    "https://careers.airbnb.com/positions/5491458",
                ),
                Job(
                    "Staff Software Engineer, Hosting Services",
                    "https://careers.airbnb.com/positions/5141000",
                ),
            ],
        ),
        "airtable": Test(
            parser.AirtableParser(),
            [
                Job(
                    "Software Engineer (Mobile, iOS)",
                    "https://boards.greenhouse.io/airtable/jobs/7017498002",
                ),
                Job(
                    "Product Manager, Data Scale",
                    "https://boards.greenhouse.io/airtable/jobs/6142546002",
                ),
            ],
        ),
        "stripe": Test(
            parser.StripeParser(),
            [
                Job(
                    "Frontend Engineer, Growth",
                    "https://stripe.com/jobs/listing/frontend-engineer-growth/5358773",
                ),
                Job(
                    "Financial Crimes Risk Assessment Lead",
                    "https://stripe.com/jobs/listing/financial-crimes-risk-assessment-lead/5466374",  # noqa: E501
                ),
            ],
        ),
    }

    for org, test in cases.items():
        html = page_reader(ORGANIZATIONS[org])
        jobs = test.parser.parse(html)

        for job in test.expected:
            assert job in jobs, f"{job} missing from result set for {org}"
