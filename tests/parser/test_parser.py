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
        # "airbnb": Test(
        #     parser.AirbnbParser(),
        #     [
        #         Job(
        #             "Senior Software Engineer, Trust Platform",
        #             "https://careers.airbnb.com/positions/5491458",
        #         ),
        #         Job(
        #             "Staff Software Engineer, Hosting Services",
        #             "https://careers.airbnb.com/positions/5141000",
        #         ),
        #     ],
        # ),
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
        # "mongodb": Test(
        #     parser.MongoDBParser(),
        #     [
        #         Job(
        #             "Senior Software Engineer, AI Code Modernisation",
        #             "https://www.mongodb.com/careers/job/?gh_jid=5382195",
        #         ),
        #         Job(
        #             "Senior Site Reliability Engineer",
        #             "https://www.mongodb.com/careers/job/?gh_jid=5403134",
        #         ),
        #     ],
        # ),
        # "pintrest": Test(
        #     parser.PintrestParser(),
        #     [
        #         Job(
        #             "Engineering Manager, SDET",
        #             "https://www.pinterestcareers.com/en/jobs/4997045/"
        #             "engineering-manager-sdet/?gh_jid=4997045",
        #         ),
        #         Job(
        #             "Staff iOS Software Engineer, Advanced Technologies Group",
        #             "https://www.pinterestcareers.com/en/jobs/5426324/"
        #             "staff-ios-software-engineer-advanced-technologies-group/"
        #             "?gh_jid=5426324",
        #         ),
        #     ],
        # ),
        # "plaid": Test(
        #     parser.PlaidParser(),
        #     [
        #         Job(
        #             "Experienced Software Engineer - Developer Efficiency",
        #             "https://plaid.com/careers/openings/engineering/"
        #             "united-states/experienced-software-engineer-developer-efficiency",
        #         ),
        #         Job(
        #             "Software Engineer - Full Stack (Credit)",
        #             "https://plaid.com/careers/openings/engineering/"
        #             "san-francisco/software-engineer-full-stack-credit",
        #         ),
        #     ],
        # ),
        # "square": Test(
        #     parser.SquareParser(),
        #     [
        #         Job(
        #             "Machine Learning Engineer (Modeling) - Customer Support",
        #             "https://www.smartrecruiters.com/Square/743999940906343",
        #         ),
        #         Job(
        #             "Fraud Risk Manager- Decision Science",
        #             "https://www.smartrecruiters.com/Square/743999943597619",
        #         ),
        #     ],
        # ),
        # "stripe": Test(
        #     parser.StripeParser(),
        #     [
        #         Job(
        #             "Frontend Engineer, Growth",
        #             "https://stripe.com/jobs/listing/frontend-engineer-growth/5358773",
        #         ),
        #         Job(
        #             "Financial Crimes Risk Assessment Lead",
        #             "https://stripe.com/jobs/listing/financial-crimes-risk-"
        #             "assessment-lead/5466374",
        #         ),
        #     ],
        # ),
        # "zscaler": Test(
        #     parser.ZscalerParser(),
        #     [
        #         Job(
        #             "Android Networking, Staff Software Engineer",
        #             "https://boards.greenhouse.io/zscaler/jobs/4090297007",
        #         ),
        #         Job(
        #             "Account Executive, Enterprise",
        #             "https://boards.greenhouse.io/zscaler/jobs/4089921007",
        #         ),
        #     ],
        # ),
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
