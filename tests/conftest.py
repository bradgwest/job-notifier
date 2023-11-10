import os

import pytest

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
PAGES_DIR = os.path.join(DATA_DIR, "pages")


@pytest.fixture
def get_page():
    def _reader(company):
        html_path = os.path.join(PAGES_DIR, f"{company}.html")
        with open(html_path) as f:
            return f.read()

    return _reader
