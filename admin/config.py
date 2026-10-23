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
    session_cookie_domain: str | None
    session_same_site: str
    public_site_url: str
    cors_origins: tuple[str, ...]

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
    cookie_domain = os.getenv("SESSION_COOKIE_DOMAIN", "").strip() or None
    on_render = os.getenv("RENDER") == "true"
    https_only = _env_truthy("SESSION_HTTPS_ONLY") or on_render or bool(cookie_domain)
    if cookie_domain:
        same_site = "none"
    else:
        same_site = "lax"

    public_site = os.getenv("PUBLIC_SITE_URL", "https://meowoo.me").rstrip("/")
    origins: list[str] = [public_site]
    extra = os.getenv("PUBLIC_SITE_ORIGINS", "")
    for part in extra.split(","):
        part = part.strip().rstrip("/")
        if part and part not in origins:
            origins.append(part)
    for local in ("http://127.0.0.1:8080", "http://localhost:8080", "http://127.0.0.1:8000"):
        if local not in origins:
            origins.append(local)

    return Settings(
        admin_password=password,
        secret_key=secret,
        github_token=os.getenv("GITHUB_TOKEN"),
        github_repo=os.getenv("GITHUB_REPO", "SwanyWu/meowoo"),
        github_branch=os.getenv("GITHUB_BRANCH", "main"),
        publish_sections=tuple(s.strip() for s in sections.split(",") if s.strip()),
        session_https_only=https_only,
        session_cookie_domain=cookie_domain,
        session_same_site=same_site,
        public_site_url=public_site,
        cors_origins=tuple(origins),
    )
