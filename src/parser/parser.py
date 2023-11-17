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
            for listing in soup.find_all(
                "a", class_="jobs-board__positions__list__item__link"
            )
        ]


class AirtableParser(Parser):
    def _parse(self, soup: BeautifulSoup) -> List[Job]:
        return [
            Job(title=listing.find("p").text.strip(), url=listing.a["href"])
            for listing in soup.find_all("div", class_="css-1tqfbpm")
        ]


class CloudflareParser(Parser):
    def _parse(self, soup: BeautifulSoup) -> List[Job]:
        return [
            Job(title=listing.a.text.strip(), url=listing.a["href"])
            for listing in soup.find_all(
                "div",
                class_="w-100 flex flex-row flex-wrap bb b--gray0 "
                "justify-center js-job-entry pt2",
            )
        ]


class MongoDBParser(Parser):
    def _parse(self, soup: BeautifulSoup) -> List[Job]:
        return [
            Job(title=listing.text.strip(), url=listing["href"])
            for listing in soup.find_all("", class_="")
        ]


class PintrestParser(Parser):
    def _parse(self, soup: BeautifulSoup) -> List[Job]:
        return [
            Job(title=listing.text.strip(), url=listing["href"])
            for listing in soup.find_all("", class_="")
        ]


class PlaidParser(Parser):
    def _parse(self, soup: BeautifulSoup) -> List[Job]:
        return [
            Job(title=listing.text.strip(), url=listing["href"])
            for listing in soup.find_all("", class_="")
        ]


class SquareParser(Parser):
    def _parse(self, soup: BeautifulSoup) -> List[Job]:
        return [
            Job(title=listing.text.strip(), url=listing["href"])
            for listing in soup.find_all("", class_="")
        ]


class StripeParser(Parser):
    def _parse(self, soup: BeautifulSoup) -> List[Job]:
        def _add_domain(url: str) -> str:
            if url.startswith("http"):
                return url
            return "https://stripe.com" + url

        return [
            Job(title=listing.text.strip(), url=_add_domain(listing["href"]))
            for listing in soup.find_all("a", class_="Link JobsListings__link")
        ]


class ZscalerParser(Parser):
    def _parse(self, soup: BeautifulSoup) -> List[Job]:
        return [
            Job(title=listing.text.strip(), url=listing["href"])
            for listing in soup.find_all("", class_="")
        ]
