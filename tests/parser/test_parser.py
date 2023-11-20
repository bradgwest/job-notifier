from typing import List, NamedTuple

from bs4 import BeautifulSoup

from src.job import Job
from src.parser import parser
from src.runner import ORGANIZATIONS, PageReader


class TestParser(parser.Parser):
    def parse(self, content: str) -> List[Job]:
        soup = BeautifulSoup(content, "lxml")
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
                    "Senior Lead, Channel Communications",
                    "https://careers.airbnb.com/positions/5505094",
                ),
                Job(
                    "Senior Systems Engineer",
                    "https://careers.airbnb.com/positions/5304422",
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
        "cloudflare": Test(
            parser.CloudflareParser(),
            [
                Job(
                    "Global Commissions Lead",
                    "https://boards.greenhouse.io/cloudflare/jobs/5479964?"
                    "gh_jid=5479964",
                ),
                Job(
                    "Senior Billing Systems Engineer",
                    "https://boards.greenhouse.io/cloudflare/jobs/5383305?"
                    "gh_jid=5383305",
                ),
            ],
        ),
        "mongodb": Test(
            parser.MongoDBParser(),
            [
                Job(
                    "Senior Product Performance Engineer",
                    "https://www.mongodb.com/careers/job/?gh_jid=5377363",
                ),
                Job(
                    "Senior Site Reliability Engineer",
                    "https://www.mongodb.com/careers/job/?gh_jid=5403134",
                ),
            ],
        ),
        "pintrest": Test(
            parser.PintrestParser(),
            [
                Job(
                    "Senior Software Engineer, Backend",
                    "https://www.pinterestcareers.com/en/jobs/5448390/"
                    "senior-software-engineer-backend/?gh_jid=5448390",
                ),
                Job(
                    "Senior Software Engineer, Backend",
                    "https://www.pinterestcareers.com/en/jobs/5448390/"
                    "senior-software-engineer-backend/?gh_jid=5448390",
                ),
            ],
        ),
        "square": Test(
            parser.SquareParser(),
            [
                Job(
                    "Senior Software Engineer, Orders Data Platform",
                    "https://jobs.smartrecruiters.com/Square/743999944959483-"
                    "senior-software-engineer-orders-data-platform",
                ),
                Job(
                    "Machine Learning Engineer, Commerce Fraud Risk (Modeling)",
                    "https://jobs.smartrecruiters.com/Square/743999944256943-"
                    "machine-learning-engineer-commerce-fraud-risk-modeling-",
                ),
            ],
        ),
        "stripe": Test(
            parser.StripeParser(),
            [
                Job(
                    "Data Engineer",
                    "https://stripe.com/jobs/listing/data-engineer/4901909",
                ),
                Job(
                    "Financial Crimes Risk Assessment Lead",
                    "https://stripe.com/jobs/listing/financial-crimes-risk-"
                    "assessment-lead/5466374",
                ),
            ],
        ),
        "zscaler": Test(
            parser.ZscalerParser(),
            [
                Job(
                    "Android Networking, Staff Software Engineer",
                    "https://boards.greenhouse.io/zscaler/jobs/4090297007",
                ),
                Job(
                    "Account Executive, Enterprise",
                    "https://boards.greenhouse.io/zscaler/jobs/4089921007",
                ),
            ],
        ),
    }

    missing_parser_tests = set(ORGANIZATIONS.keys()) - set(cases.keys())
    assert (
        not missing_parser_tests
    ), f"missing parser test(s) {sorted(missing_parser_tests)}"

    for org, test in cases.items():
        html = page_reader(ORGANIZATIONS[org])
        jobs = test.parser.parse(html)

        for job in test.expected:
            assert job in jobs, f"{job} missing from result set for {org}"
