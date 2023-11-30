import json
from typing import Callable, List, Tuple

import requests
from bs4 import BeautifulSoup

from job_notifier.job import Job

# tuple: is_next_page, job_list
PageData = Tuple[bool, List[Job]]
PageReader = Callable[[str, str], str]


def reader(org: str, url: str) -> str:
    """Read a url, returning the content."""
    r = requests.get(url)
    r.raise_for_status()
    return r.content.decode(r.encoding or "utf-8")


class Parser:
    def __init__(self, reader: PageReader = reader) -> None:
        self._reader = reader

    @property
    def org(self) -> str:
        """The organization name."""
        raise NotImplementedError

    @property
    def url(self) -> str:
        """The url to read."""
        raise NotImplementedError

    def parse(self) -> List[Job]:
        """Parse a url, following pages, returning a list of jobs."""
        jobs: List[Job] = []
        page = 1
        while True:
            content = self._reader(self.org, self.url.format(page=page))
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


class AffirmParser(Parser):
    @property
    def org(self) -> str:
        return "affirm"

    @property
    def url(self) -> str:
        return "https://boards.greenhouse.io/affirm"

    def _parse(self, content: str) -> PageData:
        soup = BeautifulSoup(content, "lxml")
        domain = "https://boards.greenhouse.io"
        return False, [
            Job(title=listing.a.text.strip(), url=f'{domain}{listing.a["href"]}')
            for listing in soup.find_all("div", class_="opening")
            if "Remote US" in listing.span.text.strip()
        ]


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


class NvidiaParser(Parser):
    JOBS_DOMAIN = "https://nvidia.wd5.myworkdayjobs.com/en-US/NVIDIAExternalCareerSite"

    @property
    def org(self) -> str:
        return "nvidia"

    @property
    def url(self) -> str:
        return (
            "https://nvidia.wd5.myworkdayjobs.com/wday/cxs/nvidia/"
            "NVIDIAExternalCareerSite/jobs"
        )

    # todo: need to paginate
    @staticmethod
    def reader(org: str, url: str) -> str:
        data = {
            "appliedFacets": {
                "locationHierarchy2": ["0c3f5f117e9a0101f63dc469c3010000"],
                "locationHierarchy1": ["2fcb99c455831013ea52fb338f2932d8"],
                "jobFamilyGroup": ["0c40f6bd1d8f10ae43ffaefd46dc7e78"],
                "workerSubType": ["0c40f6bd1d8f10adf6dae161b1844a15"],
                "timeType": ["5509c0b5959810ac0029943377d47364"],
            },
            "limit": 20,  # 20 is Max
            "offset": 0,  # todo need to paginate. Refactor required
            "searchText": "",
        }
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        r = requests.post(url, data=json.dumps(data), headers=headers)
        r.raise_for_status()
        return r.content.decode(r.encoding or "utf-8")

    def _parse(self, content: str) -> PageData:
        d = json.loads(content)
        return False, [
            Job(
                title=listing["title"].strip(),
                url=self.JOBS_DOMAIN + listing["externalPath"],
            )
            for listing in d["jobPostings"]
        ]


class RampParser(Parser):
    @property
    def org(self) -> str:
        return "ramp"

    @property
    def url(self) -> str:
        return "https://api.ashbyhq.com/posting-api/job-board/ramp"

    def _parse(self, content: str) -> PageData:
        d = json.loads(content)
        return False, [
            Job(title=job["title"].strip(), url=job["jobUrl"])
            for job in d["jobs"]
            if job["isRemote"]
            or any(
                location["location"] == "Remote"
                for location in job["secondaryLocations"]
            )
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


class VectaraParser(Parser):
    @property
    def org(self) -> str:
        return "vectara"

    @property
    def url(self) -> str:
        return "https://jobs.lever.co/vectara"

    def _parse(self, content: str) -> PageData:
        soup = BeautifulSoup(content, "lxml")
        return False, [
            Job(
                title=listing.h5.text.strip(),
                url=listing["href"],
            )
            for listing in soup.find_all("a", class_="posting-title")
            if "US Remote"
            in listing.find(
                "span",
                "sort-by-location posting-category small-category-label location",
            ).text.strip()
        ]


class ZillowParser(Parser):
    JOBS_DOMAIN = "https://zillow.wd5.myworkdayjobs.com/en-US/Zillow_Group_External"

    @property
    def org(self) -> str:
        return "zillow"

    @property
    def url(self) -> str:
        return (
            "https://zillow.wd5.myworkdayjobs.com/wday/cxs/zillow/"
            "Zillow_Group_External/jobs"
        )

    # todo: need to paginate
    @staticmethod
    def reader(org: str, url: str) -> str:
        data = {
            "appliedFacets": {
                "timeType": ["156fb9a2f01c10be203b6e91581a01d1"],  # Full Time
                "workerSubType": ["156fb9a2f01c10bed80e140d011a9559"],  # Regular
                "locations": ["bf3166a9227a01f8b514f0b00b147bc9"],  # Remote-USA
                "jobFamilyGroup": ["a90eab1aaed6105e8dd41df427a82ee6"],  # Software Dev
            },
            "limit": 20,  # 20 is Max
            "offset": 0,
            "searchText": "",
        }
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        r = requests.post(url, data=json.dumps(data), headers=headers)
        r.raise_for_status()
        return r.content.decode(r.encoding or "utf-8")

    def _parse(self, content: str) -> PageData:
        d = json.loads(content)
        return False, [
            Job(
                title=listing["title"].strip(),
                url=self.JOBS_DOMAIN + listing["externalPath"],
            )
            for listing in d["jobPostings"]
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
