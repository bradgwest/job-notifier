from src.parser.parser import Job
from src.parser.stripe import StripeParser
from src.runner import ORGANIZATIONS, PageReader


def test_stripe_parser(page_reader: PageReader):
    expected = [
        Job(
            "Frontend Engineer, Growth",
            "https://stripe.com/jobs/listing/frontend-engineer-growth/5358773",
        ),
        Job(
            "Financial Crimes Risk Assessment Lead",
            "https://stripe.com/jobs/listing/financial-crimes-risk-assessment-lead/5466374",  # noqa: E501
        ),
    ]

    parser = StripeParser()
    html = page_reader(ORGANIZATIONS["stripe"])
    jobs = parser.parse(html)

    for job in expected:
        assert job in jobs, f"{job} missing from result set"
