from src.notifier import main
from tests.storage.test_storage import TesterConfig, TesterStorage


def test_main():
    cfg = TesterConfig(path="/test/path")
    store = TesterStorage(cfg)
    assert main(store) is None
