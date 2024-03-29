import json
from typing import Any, Callable, Dict, List, Tuple

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


class GreenhouseAPIParser(Parser):
    def _parse(self, content: str) -> PageData:
        d = json.loads(content)
        return False, [
            Job(
                title=job["title"].strip(),
                url=job["absolute_url"],
            )
            for job in d["jobs"]
            if self._match(job)
        ]

    @property
    def url(self) -> str:
        return f"https://api.greenhouse.io/v1/boards/{self.org}/jobs"

    def _match(self, job: Dict[str, Any]) -> bool:
        return True


# todo
class WorkdayAPIParser(Parser):
    pass


class AffirmParser(GreenhouseAPIParser):
    @property
    def org(self) -> str:
        return "affirm"

    def _match(self, job: Dict[str, Any]) -> bool:
        return "Remote US" in job["location"]["name"]


class AirbnbParser(GreenhouseAPIParser):
    @property
    def org(self) -> str:
        return "airbnb"


class AirtableParser(GreenhouseAPIParser):
    @property
    def org(self) -> str:
        return "airtable"

    def _match(self, job: Dict[str, Any]) -> bool:
        return "Remote" in job["location"]["name"]


class ChanzuckerberginitiativeParser(GreenhouseAPIParser):
    @property
    def org(self) -> str:
        return "chanzuckerberginitiative"

    def _match(self, job: Dict[str, Any]) -> bool:
        return "Remote" in job["location"]["name"]


class CloudflareParser(GreenhouseAPIParser):
    @property
    def org(self) -> str:
        return "cloudflare"

    def _match(self, job: Dict[str, Any]) -> bool:
        return "Remote US" in job["location"]["name"]


class DiscordParser(GreenhouseAPIParser):
    @property
    def org(self) -> str:
        return "discord"

    def _match(self, job: Dict[str, Any]) -> bool:
        return "Remote" in job["location"]["name"]


class ElasticParser(GreenhouseAPIParser):
    @property
    def org(self) -> str:
        return "elastic"

    def _match(self, job: Dict[str, Any]) -> bool:
        return "United States" in job["location"]["name"]


class FigmaParser(GreenhouseAPIParser):
    @property
    def org(self) -> str:
        return "figma"

    def _match(self, job: Dict[str, Any]) -> bool:
        return "United States" in job["location"]["name"]


class LaceworkParser(GreenhouseAPIParser):
    @property
    def org(self) -> str:
        return "lacework"

    def _match(self, job: Dict[str, Any]) -> bool:
        return (
            job["location"]["name"] == "Remote - US"
            or job["location"]["name"] == "United States"
        )


class MongodbParser(GreenhouseAPIParser):
    @property
    def org(self) -> str:
        return "mongodb"

    def _match(self, job: Dict[str, Any]) -> bool:
        return "Remote North America" in job["location"]["name"]


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


class RedditParser(GreenhouseAPIParser):
    @property
    def org(self) -> str:
        return "reddit"

    def _match(self, job: Dict[str, Any]) -> bool:
        return "Remote - United States" == job["location"]["name"]


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


class SlackParser(Parser):
    JOBS_DOMAIN = "https://salesforce.wd12.myworkdayjobs.com/en-US/Slack"

    @property
    def org(self) -> str:
        return "slack"

    @property
    def url(self) -> str:
        return (
            "https://salesforce.wd12.myworkdayjobs.com/wday/cxs/salesforce/Slack/jobs"
        )

    # todo: need to paginate
    @staticmethod
    def reader(org: str, url: str) -> str:
        data = {
            "appliedFacets": {
                "CF_-_REC_-_LRV_-_Job_Posting_Anchor_-_Country_from_Job_Posting_Location_Extended": [  # noqa
                    "bc33aa3152ec42d4995f4791a106ed09"
                ],
                "jobFamilyGroup": ["14fa3452ec7c1011f90d0002a2100000"],
                "workerSubType": ["3a910852b2c31010f48d2bbc8b020000"],
            },
            "limit": 20,
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


class StitchfixParser(GreenhouseAPIParser):
    @property
    def org(self) -> str:
        return "stitchfix"

    def _match(self, job: Dict[str, Any]) -> bool:
        return job["location"]["name"] == "Remote, USA"


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


class TwilioParser(GreenhouseAPIParser):
    @property
    def org(self) -> str:
        return "twilio"

    def _match(self, job: Dict[str, Any]) -> bool:
        return job["location"]["name"] == "Remote - US"


class UpstartParser(GreenhouseAPIParser):
    @property
    def org(self) -> str:
        return "upstart"

    def _match(self, job: Dict[str, Any]) -> bool:
        return job["location"]["name"] == "United States | Remote"


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


class ZscalerParser(GreenhouseAPIParser):
    @property
    def org(self) -> str:
        return "zscaler"

    def _match(self, job: Dict[str, Any]) -> bool:
        return (
            "AMS" in job["location"]["name"]
            or "United States" in job["location"]["name"]
        )
