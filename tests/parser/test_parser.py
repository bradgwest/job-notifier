import json
from typing import List, NamedTuple

from bs4 import BeautifulSoup

from job_notifier.job import Job
from job_notifier.parser import parser
from job_notifier.runner import PARSERS


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

    parser = TestParser(lambda _, __: content)
    jobs = parser.parse()
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

    parser = TestJSONParser(reader)
    jobs = parser.parse()
    assert len(jobs) == 4
    assert jobs[0] == Job(**pages["test?page=1"]["jobs"][0])  # type: ignore
    assert jobs[3] == Job(**pages["test?page=2"]["jobs"][1])  # type: ignore


def test_org_parsers(page_reader: parser.PageReader):
    class Test(NamedTuple):
        parser: parser.Parser
        expected: List[Job]

    cases = {
        "affirm": Test(
            parser.AffirmParser(page_reader),
            [
                Job(
                    "Senior Software Engineer (Infrastructure Platform)",
                    "https://boards.greenhouse.io/affirm/jobs/5706497003",
                ),
                Job(
                    "Senior Software Engineer, Backend (ML Data)",
                    "https://boards.greenhouse.io/affirm/jobs/5761151003",
                ),
            ],
        ),
        "airbnb": Test(
            parser.AirbnbParser(page_reader),
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
            parser.AirtableParser(page_reader),
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
            parser.CloudflareParser(page_reader),
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
        "discord": Test(
            parser.DiscordParser(page_reader),
            [
                Job(
                    "Senior Software Engineer, Apps User Experience",
                    "https://boards.greenhouse.io/discord/jobs/6974294002",
                ),
                Job(
                    "Senior Software Engineer, Core Product",
                    "https://boards.greenhouse.io/discord/jobs/6969882002",
                ),
            ],
        ),
        "figma": Test(
            parser.FigmaParser(page_reader),
            [
                Job(
                    "Software Engineer - Creation Engine",
                    "https://boards.greenhouse.io/figma/jobs/4754116004",
                ),
                Job(
                    "Software Engineer - Editor",
                    "https://boards.greenhouse.io/figma/jobs/4214847004",
                ),
            ],
        ),
        "lacework": Test(
            parser.LaceworkParser(page_reader),
            [
                Job(
                    "Software Engineer - Developer Infrastructure",
                    "https://www.lacework.com/job-openings?gh_jid=4883515004",
                ),
                Job(
                    "Software Engineer - Data Foundation",
                    "https://www.lacework.com/job-openings?gh_jid=4945239004",
                ),
            ],
        ),
        "mongodb": Test(
            parser.MongoDBParser(page_reader),
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
            parser.NetflixParser(page_reader),
            [
                Job(
                    "Engineering Manager - Compute Runtime",
                    "https://jobs.netflix.com/jobs/303524654",
                ),
                Job("Art Director", "https://jobs.netflix.com/jobs/302748851"),
            ],
        ),
        "nvidia": Test(
            parser.NvidiaParser(page_reader),
            [
                Job(
                    "Principal Threat Intelligence Engineer",
                    "https://nvidia.wd5.myworkdayjobs.com/en-US/"
                    "NVIDIAExternalCareerSite"
                    "/job/US-CO-Remote/Principal-Threat-Intelligence-Engineer_"
                    "JR1976075-1",
                ),
                Job(
                    "GPU System Software Engineer",
                    "https://nvidia.wd5.myworkdayjobs.com/en-US/"
                    "NVIDIAExternalCareerSite"
                    "/job/US-TX-Austin/GPU-System-Software-Engineer_JR1969229-1",
                ),
            ],
        ),
        "pintrest": Test(
            parser.PintrestParser(page_reader),
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
        "ramp": Test(
            parser.RampParser(page_reader),
            [
                Job(
                    "Staff Software Engineer | Cloud Security",
                    "https://jobs.ashbyhq.com/ramp/"
                    "34413f8d-26bf-4bbc-8ade-eb309a0e2245",
                ),
                Job(
                    "Software Engineer | Frontend",
                    "https://jobs.ashbyhq.com/ramp/"
                    "4e64ab86-4e30-403b-b1b9-41dc052570ce",
                ),
            ],
        ),
        "reddit": Test(
            parser.RedditParser(page_reader),
            [
                Job(
                    "Staff Software Engineer, Web Platform",
                    "https://boards.greenhouse.io/reddit/jobs/5330121",
                ),
                Job(
                    "Principal Mobile Engineer, Core Experience",
                    "https://boards.greenhouse.io/reddit/jobs/5374658",
                ),
            ],
        ),
        "slack": Test(
            parser.SlackParser(page_reader),
            [
                Job(
                    "Senior Fullstack Software Engineer, Quip",
                    "https://salesforce.wd12.myworkdayjobs.com/en-US/Slack/job"
                    "/Colorado---Remote/Senior-Fullstack-Software-Engineer--"
                    "Quip_JR218178-2",
                ),
                Job(
                    "Security Engineer - Slack",
                    "https://salesforce.wd12.myworkdayjobs.com/en-US/Slack/job"
                    "/Colorado---Remote/Security-Engineer---Slack_JR231535",
                ),
            ],
        ),
        "square": Test(
            parser.SquareParser(page_reader),
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
            parser.StripeParser(page_reader),
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
        "twilio": Test(
            parser.TwilioParser(page_reader),
            [
                Job(
                    "Principal Fullstack Engineer",
                    "https://boards.greenhouse.io/twilio/jobs/5543642",
                ),
                Job(
                    "Senior Fullstack Engineer",
                    "https://boards.greenhouse.io/twilio/jobs/5565685",
                ),
            ],
        ),
        "upstart": Test(
            parser.UpstartParser(page_reader),
            [
                Job(
                    "Data Platform Engineer",
                    "https://www.upstart.com/careers/5499985/apply?gh_jid=5499985",
                ),
                Job(
                    "Full Stack Software Engineer, Pricing",
                    "https://www.upstart.com/careers/5461095/apply?gh_jid=5461095",
                ),
            ],
        ),
        "vectara": Test(
            parser.VectaraParser(page_reader),
            [
                Job(
                    "Software Engineer",
                    "https://jobs.lever.co/vectara/"
                    "f5d5286b-6202-4d4b-b2e4-36101d142c6c",
                ),
                Job(
                    "Product Manager",
                    "https://jobs.lever.co/vectara/"
                    "ff439929-ae7b-45a5-9656-7ee1e71b1aed",
                ),
            ],
        ),
        "zillow": Test(
            parser.ZillowParser(page_reader),
            [
                Job(
                    "Senior Software Development Engineer, Big Data",
                    "https://zillow.wd5.myworkdayjobs.com/en-US/Zillow_Group_External"
                    "/job/Remote-USA/Senior-Software-Development-Engineer--"
                    "Big-Data_P743363-1",
                ),
                Job(
                    "Senior Principal Big Data Architect",
                    "https://zillow.wd5.myworkdayjobs.com/en-US/Zillow_Group_External"
                    "/job/Remote-USA/Senior-Principal-Big-Data-Architect_P741689-1",
                ),
            ],
        ),
        "zscaler": Test(
            parser.ZscalerParser(page_reader),
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

    assert list(PARSERS.keys()) == list(sorted(PARSERS.keys())), "PARSERS is not sorted"
    assert list(cases.keys()) == list(sorted(cases.keys())), "cases is not sorted"
    assert set(PARSERS.keys()) == set(
        cases.keys()
    ), "PARSERS and cases do not match. Either missing a test case or a parser."

    for org, test in cases.items():
        jobs = test.parser.parse()

        for job in test.expected:
            assert job in jobs, f"{job} missing from result set for {org}"
