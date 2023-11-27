from job_notifier.storage.storage import Storage


def test_storage(storage: Storage):
    org = "org"

    for page in storage.LISTINGS:  # type: ignore
        storage.write(org, page)  # type: ignore

    pages = list(storage.read(org))
    pages.reverse()
    assert pages == storage.LISTINGS  # type: ignore
