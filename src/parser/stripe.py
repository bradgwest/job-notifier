from typing import List

from bs4 import BeautifulSoup

from src.job import Job
from src.parser.parser import Parser


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
