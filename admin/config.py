from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

from publisher.github_client import GitHubConfig

load_dotenv()


def _env_truthy(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.lower() in ("1", "true", "yes", "on")


@dataclass
class Settings:
    admin_password: str
    secret_key: str
    github_token: str | None
    github_repo: str
    github_branch: str
    publish_sections: tuple[str, ...]
    session_https_only: bool

    @property
    def github_enabled(self) -> bool:
        return bool(self.github_token and self.github_repo)

    def github_config(self) -> GitHubConfig | None:
        if not self.github_enabled:
            return None
        return GitHubConfig.from_repo_env(
            self.github_token,  # type: ignore[arg-type]
            self.github_repo,
            self.github_branch,
        )


def get_settings() -> Settings:
    password = os.getenv("ADMIN_PASSWORD")
    secret = os.getenv("SECRET_KEY")
    if not password:
        raise RuntimeError("ADMIN_PASSWORD is not set")
    if not secret:
        raise RuntimeError("SECRET_KEY is not set")

    sections = os.getenv("PUBLISH_SECTIONS", "ramble")
    https_only = _env_truthy("SESSION_HTTPS_ONLY") or os.getenv("RENDER") == "true"
    return Settings(
        admin_password=password,
        secret_key=secret,
        github_token=os.getenv("GITHUB_TOKEN"),
        github_repo=os.getenv("GITHUB_REPO", "SwanyWu/meowoo"),
        github_branch=os.getenv("GITHUB_BRANCH", "main"),
        publish_sections=tuple(s.strip() for s in sections.split(",") if s.strip()),
        session_https_only=https_only,
    )
