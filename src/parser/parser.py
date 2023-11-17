from typing import List

from bs4 import BeautifulSoup

from src.job import Job


class Parser:
    def parse(self, content: str) -> List[Job]:
        soup = BeautifulSoup(content, "lxml")
        return self._parse(soup)

    def _parse(self, soup: BeautifulSoup) -> List[Job]:
        raise NotImplementedError


class AirbnbParser(Parser):
    def _parse(self, soup: BeautifulSoup) -> List[Job]:
        return [
            Job(title=listing.text.strip(), url=listing["href"])
            for listing in soup.find_all("a")
            if listing.get("href", "").startswith(
                "https://careers.airbnb.com/positions/"
            )
        ]


class AirtableParser(Parser):
    def _parse(self, soup: BeautifulSoup) -> List[Job]:
        return [
            Job(title=listing.p.text.strip(), url=listing["href"])
            for listing in soup.find_all("a")
            if listing.get("href", "").startswith(
                "https://boards.greenhouse.io/airtable/jobs/"
            )
        ]


class CloudflareParser(Parser):
    def _parse(self, soup: BeautifulSoup) -> List[Job]:
        return [
            Job(title=listing.text.strip(), url=listing["href"])
            for listing in soup.find_all("a")
            if listing
            and listing.get("href", "").startswith(
                "https://boards.greenhouse.io/cloudflare/jobs/"
            )
        ]


class MongoDBParser(Parser):
    def _parse(self, soup: BeautifulSoup) -> List[Job]:
        return [
            Job(title=listing.div.span.text.strip(), url=listing["href"])
            for listing in soup.find_all("a")
            if listing.get("href", "").startswith(
                "https://www.mongodb.com/careers/job/?"
            )
        ]


class PintrestParser(Parser):
    def _parse(self, soup: BeautifulSoup) -> List[Job]:
        return [
            Job(title=listing.text.strip(), url=listing["href"])
            for listing in soup.find_all("a")
            if listing.get("href", "").startswith(
                "https://www.pinterestcareers.com/en/jobs/"
            )
        ]


class PlaidParser(Parser):
    def _parse(self, soup: BeautifulSoup) -> List[Job]:
        return [
            Job(title=listing.p.text.strip(), url=listing["href"])
            for listing in soup.find_all("a")
            if listing.get("href", "").startswith("https://plaid.com/careers/openings/")
        ]


class SquareParser(Parser):
    def _parse(self, soup: BeautifulSoup) -> List[Job]:
        return [
            Job(title=listing.text.strip(), url=listing["href"])
            for listing in soup.find_all("a")
            if listing.get("href", "").startswith(
                "https://www.smartrecruiters.com/Square/"
            )
        ]


class StripeParser(Parser):
    def _parse(self, soup: BeautifulSoup) -> List[Job]:
        return [
            Job(title=listing.text.strip(), url=listing["href"])
            for listing in soup.find_all("a")
            if listing.get("href", "").startswith("https://stripe.com/jobs/listing")
            or listing.get("href", "").startswith("jobs/listing")
        ]


class ZscalerParser(Parser):
    def _parse(self, soup: BeautifulSoup) -> List[Job]:
        return [
            Job(title=listing.div.div.text.strip(), url=listing["href"])
            for listing in soup.find_all("a")
            if listing.get("href", "").startswith(
                "https://boards.greenhouse.io/zscaler/jobs/"
            )
        ]
