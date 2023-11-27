import pathlib
import time

from job_notifier.job import Job
from job_notifier.storage.local import LocalStorage, LocalStorageConfig


def test_local_storage(tmp_path: pathlib.Path):
    LISTINGS = [
        [
            Job("Aircraft Engineer", "https://aircraft-engineers.com/jobs"),
        ],
        [
            Job("Aircraft Engineer", "https://aircraft-engineers.com/jobs"),
            Job("Mechanical Engineer", "https://mechanical-engineers.com/jobs"),
        ],
        [
            Job("Aircraft Engineer", "https://aircraft-engineers.com/jobs"),
            Job("Mechanical Engineer", "https://mechanical-engineers.com/jobs"),
            Job("GPS Engineer", "https://gps-engineers.com/jobs"),
        ],
    ]

    directory = tmp_path / "test"
    directory.mkdir()

    config = LocalStorageConfig(path=str(directory))
    storage = LocalStorage(config)

    # validate that read handles non-existent orgs
    pages = list(storage.read("org"))
    assert not pages

    for page in LISTINGS:
        time.sleep(0.1)  # ensure each page has a different timestamp
        storage.write("org", page)

    pages = list(storage.read("org"))
    # pages should be in reverse chronological order
    assert pages[0] == LISTINGS[2]
    assert pages[1] == LISTINGS[1]
    assert pages[2] == LISTINGS[0]
