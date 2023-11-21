import argparse
import json
from typing import Any, Tuple

import requests


def download(org: str, url: str) -> str:
    r = requests.get(url)
    r.raise_for_status()
    return r.content.decode(r.encoding or "utf-8")


def is_json(content: str) -> Tuple[bool, Any]:
    try:
        return True, json.loads(content)
    except json.JSONDecodeError:
        return False, ""


def save(org: str, content: str) -> None:
    write_json = False
    try:
        content = json.loads(content)
        write_json = True
    except json.JSONDecodeError:
        pass

    with open(f"tests/data/listings/{org}.txt", "w") as f:
        if write_json:
            json.dump(content, f, indent=2)
        else:
            f.write(content)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("org", help="organization to download")
    parser.add_argument("url", help="url to download")
    args = parser.parse_args()

    txt = download(args.org, args.url)
    save(args.org, txt)
