import json
from typing import Callable, List, Tuple

from bs4 import BeautifulSoup

from job_notifier.job import Job

# tuple: is_next_page, job_list
PageData = Tuple[bool, List[Job]]
PageReader = Callable[[str, str], str]


class Parser:
    @property
    def org(self) -> str:
        """The organization name."""
        raise NotImplementedError

    @property
    def url(self) -> str:
        """The url to read."""
        raise NotImplementedError

    def parse(self, reader: PageReader) -> List[Job]:
        """Parse a url, following pages, returning a list of jobs."""
        jobs: List[Job] = []
        page = 1
        while True:
            content = reader(self.org, self.url.format(page=page))
            next_page, page_jobs = self._parse(content)
            jobs.extend(page_jobs)
            if not next_page:
                break
            page += 1
        return jobs

    def _parse(self, content: str) -> PageData:
        """Parse a page of content

        Returns a tuple of the next page url and a list of jobs included in
        the existing page."""
        raise NotImplementedError


class AirbnbParser(Parser):
    @property
    def org(self) -> str:
        return "airbnb"

    @property
    def url(self) -> str:
        return (
            "https://careers.airbnb.com/wp-admin/admin-ajax.php?"
            "action=fetch_greenhouse_jobs&which-board=airbnb&strip-empty=true"
        )

    def _parse(self, content: str) -> PageData:
        d = json.loads(content)
        return False, [
            Job(
                title=job["title"].strip(),
                url=f"https://careers.airbnb.com/positions/{job['id']}",
            )
            for job in d["jobs"]
            if job["location"] == "United States"
        ]


class AirtableParser(Parser):
    @property
    def org(self) -> str:
        return "airtable"

    @property
    def url(self) -> str:
        return "https://boards.greenhouse.io/airtable"

    def _parse(self, content: str) -> PageData:
        soup = BeautifulSoup(content, "lxml")
        domain = "https://boards.greenhouse.io"
        return False, [
            Job(title=listing.a.text.strip(), url=f'{domain}{listing.a["href"]}')
            for listing in soup.find_all("div", class_="opening")
        ]


class CloudflareParser(Parser):
    @property
    def org(self) -> str:
        return "cloudflare"

    @property
    def url(self) -> str:
        return "https://boards-api.greenhouse.io/v1/boards/cloudflare/offices/"

    def _parse(self, content: str) -> PageData:
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
        return False, jobs


class MongoDBParser(Parser):
    @property
    def org(self) -> str:
        return "mongodb"

    @property
    def url(self) -> str:
        return "https://api.greenhouse.io/v1/boards/mongodb/jobs?content=true"

    def _parse(self, content: str) -> PageData:
        d = json.loads(content)
        return False, [
            Job(title=job["title"].strip(), url=job["absolute_url"])
            for job in d["jobs"]
            if "Remote North America" in job["location"]["name"]
        ]


class NetflixParser(Parser):
    @property
    def org(self) -> str:
        return "netflix"

    @property
    def url(self) -> str:
        return (
            "https://jobs.netflix.com/api/search?q=Engineer&page={page}&"
            "location=Remote%2C%20United%20States"
        )

    def _parse(self, content: str) -> PageData:
        d = json.loads(content)
        has_next_page = int(d["info"]["postings"]["current_page"]) < int(
            d["info"]["postings"]["num_pages"]
        )
        return has_next_page, [
            Job(
                listing["text"].strip(),
                f'https://jobs.netflix.com/jobs/{listing["external_id"]}',
            )
            for listing in d["records"]["postings"]
        ]


class PintrestParser(Parser):
    @property
    def org(self) -> str:
        return "pintrest"

    @property
    def url(self) -> str:
        return "https://www.pinterestcareers.com/en/jobs/"

    def _parse(self, content: str) -> PageData:
        soup = BeautifulSoup(content, "lxml")
        return False, [
            Job(
                title=listing.a.text.strip(),
                url=f'https://www.pinterestcareers.com{listing.a["href"]}',
            )
            for listing in soup.find_all("div", class_="card card-job")
        ]


class SquareParser(Parser):
    @property
    def org(self) -> str:
        return "square"

    @property
    def url(self) -> str:
        return "https://careers.smartrecruiters.com/Square?remoteLocation=true"

    def _parse(self, content: str) -> PageData:
        soup = BeautifulSoup(content, "lxml")
        return False, [
            Job(title=listing.h4.text.strip(), url=listing["href"])
            for listing in soup.find_all("a", class_="link--block details")
        ]


class StripeParser(Parser):
    @property
    def org(self) -> str:
        return "stripe"

    @property
    def url(self) -> str:
        return (
            "https://stripe.com/jobs/search?remote_locations=North+America--US+Remote"
        )

    def _parse(self, content: str) -> PageData:
        soup = BeautifulSoup(content, "lxml")
        return False, [
            Job(title=listing.text.strip(), url=f'https://stripe.com{listing["href"]}')
            for listing in soup.find_all("a")
            if listing.get("data-js-target-list") == "JobsListings.listingLinks"
        ]


class ZscalerParser(Parser):
    @property
    def org(self) -> str:
        return "zscaler"

    @property
    def url(self) -> str:
        return "https://boards.greenhouse.io/zscaler"

    def _parse(self, content: str) -> PageData:
        soup = BeautifulSoup(content, "lxml")
        return False, [
            Job(
                title=listing.a.text.strip(),
                url=f'https://boards.greenhouse.io{listing.a["href"]}',
            )
            for listing in soup.find_all("div", class_="opening")
            if "Remote" in listing.span.text.strip()
            or "AMS" in listing.span.text.strip()
        ]
