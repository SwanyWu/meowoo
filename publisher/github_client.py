"""Commit multiple files to GitHub in a single commit."""

from __future__ import annotations

from dataclasses import dataclass

import httpx

API = "https://api.github.com"


@dataclass
class GitHubConfig:
    token: str
    owner: str
    repo: str
    branch: str = "main"

    @classmethod
    def from_repo_env(cls, token: str, repo: str, branch: str = "main") -> GitHubConfig:
        if "/" not in repo:
            raise ValueError("GITHUB_REPO must be owner/name")
        owner, name = repo.split("/", 1)
        return cls(token=token, owner=owner, repo=name, branch=branch)


class GitHubError(Exception):
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


def _headers(token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def commit_files(
    cfg: GitHubConfig,
    message: str,
    files: dict[str, str],
    delete_paths: list[str] | None = None,
) -> str:
    """
    Create one commit on cfg.branch updating all paths (repo-root relative).
    Returns the new commit SHA.
    """
    deletes = delete_paths or []
    if not files and not deletes:
        raise GitHubError("No files to commit")

    with httpx.Client(timeout=60.0) as client:
        h = _headers(cfg.token)
        base_url = f"{API}/repos/{cfg.owner}/{cfg.repo}"

        ref_resp = client.get(f"{base_url}/git/ref/heads/{cfg.branch}", headers=h)
        if ref_resp.status_code != 200:
            raise GitHubError(ref_resp.text, ref_resp.status_code)
        base_commit_sha = ref_resp.json()["object"]["sha"]

        commit_resp = client.get(f"{base_url}/git/commits/{base_commit_sha}", headers=h)
        if commit_resp.status_code != 200:
            raise GitHubError(commit_resp.text, commit_resp.status_code)
        base_tree_sha = commit_resp.json()["tree"]["sha"]

        tree_items = [
            {"path": path, "mode": "100644", "type": "blob", "content": content}
            for path, content in sorted(files.items())
        ]
        for path in sorted(deletes):
            tree_items.append({"path": path, "mode": "100644", "type": "blob", "sha": None})
        tree_resp = client.post(
            f"{base_url}/git/trees",
            headers=h,
            json={"base_tree": base_tree_sha, "tree": tree_items},
        )
        if tree_resp.status_code != 201:
            raise GitHubError(tree_resp.text, tree_resp.status_code)
        new_tree_sha = tree_resp.json()["sha"]

        new_commit_resp = client.post(
            f"{base_url}/git/commits",
            headers=h,
            json={
                "message": message,
                "tree": new_tree_sha,
                "parents": [base_commit_sha],
            },
        )
        if new_commit_resp.status_code != 201:
            raise GitHubError(new_commit_resp.text, new_commit_resp.status_code)
        new_commit_sha = new_commit_resp.json()["sha"]

        update_ref = client.patch(
            f"{base_url}/git/refs/heads/{cfg.branch}",
            headers=h,
            json={"sha": new_commit_sha, "force": False},
        )
        if update_ref.status_code != 200:
            raise GitHubError(update_ref.text, update_ref.status_code)

        return new_commit_sha
