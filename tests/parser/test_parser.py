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
                    "Senior Machine Learning Engineer (ML Fraud)",
                    "https://boards.greenhouse.io/affirm/jobs/5798895003",
                ),
                Job(
                    "Senior Software Engineer, Backend (Fraud Decisioning)",
                    "https://boards.greenhouse.io/affirm/jobs/5807963003",
                ),
            ],
        ),
        "airbnb": Test(
            parser.AirbnbParser(page_reader),
            [
                Job(
                    "Senior Software Engineer, Identity Infrastructure",
                    "https://careers.airbnb.com/positions/?gh_jid=4880087",
                ),
                Job(
                    "Senior Software Engineer, Trust Platform",
                    "https://careers.airbnb.com/positions/?gh_jid=5491458",
                ),
            ],
        ),
        "airtable": Test(
            parser.AirtableParser(page_reader),
            [
                Job(
                    "Senior Software Engineer",
                    "https://boards.greenhouse.io/airtable/jobs/7030001002",
                ),
                Job(
                    "Data Engineer",
                    "https://boards.greenhouse.io/airtable/jobs/7050364002",
                ),
            ],
        ),
        "chanzuckerberginitiative": Test(
            parser.ChanzuckerberginitiativeParser(page_reader),
            [
                Job(
                    "Senior Software Engineer, Science",
                    "https://boards.greenhouse.io/chanzuckerberginitiative/"
                    "jobs/5316149?gh_jid=5316149",
                ),
                Job(
                    "Senior Machine Learning Engineer, Science",
                    "https://boards.greenhouse.io/chanzuckerberginitiative/"
                    "jobs/5366977?gh_jid=5366977",
                ),
            ],
        ),
        "cloudflare": Test(
            parser.CloudflareParser(page_reader),
            [
                Job(
                    "Customer Solutions Engineer",
                    "https://boards.greenhouse.io/cloudflare/jobs/5549725"
                    "?gh_jid=5549725",
                ),
                Job(
                    "Director of Product - Data Platform",
                    "https://boards.greenhouse.io/cloudflare/jobs/5603527"
                    "?gh_jid=5603527",
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
        "elastic": Test(
            parser.ElasticParser(page_reader),
            [
                Job(
                    "Commercial Select Account Executive - Bay Area",
                    "https://jobs.elastic.co/jobs/?gh_jid=5567152",
                ),
                Job(
                    "Director - Diversity, Equity & Inclusion",
                    "https://jobs.elastic.co/jobs/?gh_jid=5569136",
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
            parser.MongodbParser(page_reader),
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
        # "pintrest": Test(
        #     parser.PintrestParser(page_reader),
        #     [
        #         Job(
        #             "Senior Software Engineer, Backend",
        #             "https://www.pinterestcareers.com/en/jobs/5448390/"
        #             "senior-software-engineer-backend/?gh_jid=5448390",
        #         ),
        #         Job(
        #             "Senior Software Engineer, Backend",
        #             "https://www.pinterestcareers.com/en/jobs/5448390/"
        #             "senior-software-engineer-backend/?gh_jid=5448390",
        #         ),
        #     ],
        # ),
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
        "stitchfix": Test(
            parser.StitchfixParser(page_reader),
            [
                Job(
                    "Data Platform Engineer",
                    "https://www.stitchfix.com/careers/jobs?gh_jid=5533179&"
                    "gh_jid=5533179",
                ),
                Job(
                    "Lead Software Engineer - Discover",
                    "https://www.stitchfix.com/careers/jobs?gh_jid=5550306&"
                    "gh_jid=5550306",
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
                    "Data Engineer",
                    "https://boards.greenhouse.io/zscaler/jobs/4101969007",
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
