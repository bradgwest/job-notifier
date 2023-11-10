from src.parsers.parser import Job
from src.parsers.stripe import StripeParser


def test_stripe_parser(get_page):
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
    html = get_page(parser.COMPANY)
    jobs = parser.parse(html)

    for job in expected:
        assert job in jobs, f"{job} missing from result set"
