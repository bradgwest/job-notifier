import os

import pytest

from src.org import Org
from src.runner import PageReader

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
PAGES_DIR = os.path.join(DATA_DIR, "pages")


@pytest.fixture
def page_reader() -> PageReader:
    def _reader(org: Org) -> str:
        html_path = os.path.join(PAGES_DIR, f"{org.name}.html")
        with open(html_path) as f:
            return f.read()

    return _reader


# todo: Add TestNotifier, TestStorage
