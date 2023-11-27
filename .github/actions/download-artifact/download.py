"""Download the latest Github artifact from a repository."""

import argparse
import io
import os
import zipfile
from typing import Any, Dict, Optional

import requests


class Github:
    URL = "https://api.github.com"

    def __init__(
        self, token: str, repo: str, branch: str, artifact_name: str, path: str
    ) -> None:
        self.repo = repo
        self.branch = branch
        self.artifact_name = artifact_name
        self.path = path
        self.session = self._build_session(token)

    def _build_session(self, token: str) -> requests.Session:
        s = requests.Session()
        s.headers.update(
            {
                "Authorization": f"token {token}",
                "X-GitHub-Api-Version": "2022-11-28",
                "Accept": "application/vnd.github+json",
            }
        )
        return s

    def _request(self, verb: str, endpoint: str, **kwargs: Any) -> requests.Response:
        url = os.path.join(self.URL, endpoint)
        r = self.session.request(verb, url, **kwargs)  # type: ignore
        r.raise_for_status()
        return r

    def _most_recent(self) -> Optional[Dict[str, Any]]:
        """Download the latest artifact for the branch"""
        list_endpoint = f"repos/{self.repo}/actions/artifacts"
        r = self._request(
            "GET", list_endpoint, params={"name": self.artifact_name, "per_page": 100}
        )
        data = r.json()
        if len(data["artifacts"]) != data["total_count"]:
            raise RuntimeError("You need to implement pagination")

        if not data["artifacts"]:
            print("No artifacts found")
            return

        return sorted(
            [
                a
                for a in data["artifacts"]
                if a["workflow_run"]["head_branch"] == self.branch
            ],
            key=lambda x: x["updated_at"],
            reverse=True,
        )[0]

    def download(self) -> None:
        artifact = self._most_recent()
        if not artifact:
            return

        download_endpoint = f"repos/{self.repo}/actions/artifacts/{artifact['id']}/zip"
        r = self._request("GET", download_endpoint)
        z = zipfile.ZipFile(io.BytesIO(r.content))
        z.extractall(self.path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--token", required=True)
    parser.add_argument("--artifact-name", required=True)
    parser.add_argument("--path", default=os.getenv("GITHUB_WORKSPACE"))
    parser.add_argument("--repo", default=os.getenv("GITHUB_REPOSITORY"))
    parser.add_argument("--branch", default=os.getenv("GITHUB_REF_NAME"))
    args = parser.parse_args()

    if not args.path:
        raise ValueError("path is required, or set GITHUB_WORKSPACE env var")

    if not args.repo:
        raise ValueError("repo is required, or set GITHUB_REPOSITORY env var")

    if not args.branch:
        raise ValueError("branch is required, or set GITHUB_REF_NAME env var")

    gh = Github(args.token, args.repo, args.branch, args.artifact_name, args.path)
    gh.download()
