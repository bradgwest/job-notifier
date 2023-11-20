import json
from typing import List

from bs4 import BeautifulSoup

from src.job import Job


class Parser:
    def parse(self, content: str) -> List[Job]:
        raise NotImplementedError


class AirbnbParser(Parser):
    def parse(self, content: str) -> List[Job]:
        d = json.loads(content)
        return [
            Job(
                title=job["title"].strip(),
                url=f"https://careers.airbnb.com/positions/{job['id']}",
            )
            for job in d["jobs"]
            if job["location"] == "United States"
        ]


class AirtableParser(Parser):
    def parse(self, content: str) -> List[Job]:
        soup = BeautifulSoup(content, "lxml")
        domain = "https://boards.greenhouse.io"
        return [
            Job(title=listing.a.text.strip(), url=f'{domain}{listing.a["href"]}')
            for listing in soup.find_all("div", class_="opening")
        ]


class CloudflareParser(Parser):
    def parse(self, content: str) -> List[Job]:
        d = json.loads(content)
        jobs: List[Job] = []
        for office in d["offices"]:
            if office["name"] != "Remote US":
                continue
            for department in office["departments"]:
                jobs.extend(
                    [
                        Job(
                            title=job["title"].strip(),
                            url=job["absolute_url"],
                        )
                        for job in department["jobs"]
                    ]
                )
        return jobs


class MongoDBParser(Parser):
    def parse(self, content: str) -> List[Job]:
        d = json.loads(content)
        return [
            Job(title=job["title"].strip(), url=job["absolute_url"])
            for job in d["jobs"]
            if "Remote North America" in job["location"]["name"]
        ]


class PintrestParser(Parser):
    def parse(self, content: str) -> List[Job]:
        soup = BeautifulSoup(content, "lxml")
        return [
            Job(
                title=listing.a.text.strip(),
                url=f'https://www.pinterestcareers.com{listing.a["href"]}',
            )
            for listing in soup.find_all("div", class_="card card-job")
        ]


class SquareParser(Parser):
    def parse(self, content: str) -> List[Job]:
        soup = BeautifulSoup(content, "lxml")
        return [
            Job(title=listing.h4.text.strip(), url=listing["href"])
            for listing in soup.find_all("a", class_="link--block details")
        ]


class StripeParser(Parser):
    def parse(self, content: str) -> List[Job]:
        soup = BeautifulSoup(content, "lxml")
        return [
            Job(title=listing.text.strip(), url=f'https://stripe.com{listing["href"]}')
            for listing in soup.find_all("a")
            if listing.get("data-js-target-list") == "JobsListings.listingLinks"
        ]


class ZscalerParser(Parser):
    def parse(self, content: str) -> List[Job]:
        soup = BeautifulSoup(content, "lxml")
        return [
            Job(
                title=listing.a.text.strip(),
                url=f'https://boards.greenhouse.io{listing.a["href"]}',
            )
            for listing in soup.find_all("div", class_="opening")
            if "Remote" in listing.span.text.strip()
            or "AMS" in listing.span.text.strip()
        ]
