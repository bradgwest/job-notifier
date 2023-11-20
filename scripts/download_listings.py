import argparse

import requests


def download(org: str, url: str) -> str:
    r = requests.get(url)
    r.raise_for_status()
    return r.content.decode(r.encoding or "utf-8")


def save(org: str, content: str) -> None:
    with open(f"tests/data/listings/{org}.txt", "w") as f:
        f.write(content)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("org", help="organization to download")
    parser.add_argument("url", help="url to download")
    args = parser.parse_args()

    html = download(args.org, args.url)
    save(args.org, html)
