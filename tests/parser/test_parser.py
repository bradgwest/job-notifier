import json
from typing import List, NamedTuple

from bs4 import BeautifulSoup

from src.job import Job
from src.parser import parser
from src.runner import PARSERS


class TestParser(parser.Parser):
    @property
    def org(self) -> str:
        return "test"

    @property
    def url(self) -> str:
        return "url"

    def _parse(self, content: str) -> parser.PageData:
        soup = BeautifulSoup(content, "lxml")
        return False, [
            Job(title=job.text.strip(), url=job["href"]) for job in soup.find_all("job")
        ]


class TestJSONParser(parser.Parser):
    @property
    def org(self) -> str:
        return "org"

    @property
    def url(self) -> str:
        return "test?page={page}"

    def _parse(self, content: str) -> parser.PageData:
        d = json.loads(content)
        return d["has_next_page"], [Job(**job) for job in d["jobs"]]


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
    jobs = parser.parse(lambda _, __: content)
    assert len(jobs) == 2
    assert jobs[0] == Job(
        title="Engineer of Chairs", url="https://company_1.com/jobs/1"
    )
    assert jobs[1] == Job(
        title="Cake Manufacturing Engineer", url="https://company_1.com/jobs/2"
    )


def test_multi_page_parser():
    pages = {
        "test?page=1": {
            "jobs": [
                Job("Engineer of Chairs", "https://company_1.com/jobs/1").to_dict(),
                Job(
                    "Cake Manufacturing Engineer", "https://company_1.com/jobs/2"
                ).to_dict(),
            ],
            "has_next_page": True,
        },
        "test?page=2": {
            "jobs": [
                Job("Consciousness Engineer", "https://company_1.com/jobs/3").to_dict(),
                Job(
                    "Engineer of Time and Space", "https://company_1.com/jobs/4"
                ).to_dict(),
            ],
            "has_next_page": False,
        },
    }

    def reader(org: str, url: str) -> str:
        return json.dumps(pages[url])

    parser = TestJSONParser()
    jobs = parser.parse(reader)
    assert len(jobs) == 4
    assert jobs[0] == Job(**pages["test?page=1"]["jobs"][0])  # type: ignore
    assert jobs[3] == Job(**pages["test?page=2"]["jobs"][1])  # type: ignore


def test_org_parsers(page_reader: parser.PageReader):
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
        "netflix": Test(
            parser.NetflixParser(),
            [
                Job(
                    "Engineering Manager - Compute Runtime",
                    "https://jobs.netflix.com/jobs/303524654",
                ),
                Job("Art Director", "https://jobs.netflix.com/jobs/302748851"),
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

    missing_parser_tests = set(PARSERS.keys()) - set(cases.keys())
    assert (
        not missing_parser_tests
    ), f"missing parser test(s) {sorted(missing_parser_tests)}"

    for org, test in cases.items():
        jobs = test.parser.parse(page_reader)

        for job in test.expected:
            assert job in jobs, f"{job} missing from result set for {org}"
