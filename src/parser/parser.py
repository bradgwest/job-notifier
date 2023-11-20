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
            Job(title=listing.text.strip(), url=listing["href"])
            for listing in soup.find_all("a")
            if listing.get("href", "").startswith(
                "https://www.pinterestcareers.com/en/jobs/"
            )
        ]


class PlaidParser(Parser):
    def parse(self, content: str) -> List[Job]:
        soup = BeautifulSoup(content, "lxml")
        return [
            Job(title=listing.p.text.strip(), url=listing["href"])
            for listing in soup.find_all("a")
            if listing.get("href", "").startswith("https://plaid.com/careers/openings/")
        ]


class SquareParser(Parser):
    def parse(self, content: str) -> List[Job]:
        soup = BeautifulSoup(content, "lxml")
        return [
            Job(title=listing.text.strip(), url=listing["href"])
            for listing in soup.find_all("a")
            if listing.get("href", "").startswith(
                "https://www.smartrecruiters.com/Square/"
            )
        ]


class StripeParser(Parser):
    def parse(self, content: str) -> List[Job]:
        soup = BeautifulSoup(content, "lxml")
        return [
            Job(title=listing.text.strip(), url=listing["href"])
            for listing in soup.find_all("a")
            if listing.get("href", "").startswith("https://stripe.com/jobs/listing")
            or listing.get("href", "").startswith("jobs/listing")
        ]


class ZscalerParser(Parser):
    def parse(self, content: str) -> List[Job]:
        soup = BeautifulSoup(content, "lxml")
        return [
            Job(title=listing.div.div.text.strip(), url=listing["href"])
            for listing in soup.find_all("a")
            if listing.get("href", "").startswith(
                "https://boards.greenhouse.io/zscaler/jobs/"
            )
        ]
