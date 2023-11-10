from typing import List

from bs4 import BeautifulSoup

from src.parsers.parser import Job, Parser


class StripeParser(Parser):
    COMPANY = "stripe"

    def _parse(self, soup: BeautifulSoup) -> List[Job]:
        return [
            Job(title=listing.text.strip(), url=listing["href"])
            for listing in soup.find_all("a", class_="Link JobsListings__link")
        ]
