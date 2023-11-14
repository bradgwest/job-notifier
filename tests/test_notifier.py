from src.notifier import main
from tests.storage.test_storage import TesterStorage


def test_main():
    assert main(TesterStorage) is None
