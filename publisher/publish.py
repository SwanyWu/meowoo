"""Write locally and push built site files to GitHub."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

from publisher.build import CONTENT_DIR, ROOT, build_section, collect_section_build_outputs
from publisher.content import compose_post_markdown, slugify
from publisher.github_client import GitHubConfig, GitHubError, commit_files
from publisher.build import load_sections


@dataclass
class PublishDraft:
    section: str
    title: str
    body: str
    excerpt: str
    post_date: date
    slug: str | None = None
    description: str | None = None
    post_vibe: str | None = None
    page_class: str | None = None
    subtitle: str | None = None
    tags: list[str] | None = None
    push_github: bool = True


@dataclass
class PublishResult:
    slug: str
    markdown_path: Path
    written_paths: list[Path]
    commit_sha: str | None
    github_pushed: bool


def publish_post(draft: PublishDraft, github: GitHubConfig | None) -> PublishResult:
    sections = load_sections()
    if draft.section not in sections:
        raise ValueError(f"Unknown section: {draft.section}")

    slug = (draft.slug or slugify(draft.title)).strip()
    if not slug:
        raise ValueError("Could not derive slug from title")

    md_text = compose_post_markdown(
        title=draft.title,
        post_date=draft.post_date,
        excerpt=draft.excerpt,
        body=draft.body,
        description=draft.description,
        post_vibe=draft.post_vibe,
        page_class=draft.page_class,
        subtitle=draft.subtitle,
        tags=draft.tags,
    )

    md_path = CONTENT_DIR / draft.section / f"{slug}.md"
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(md_text, encoding="utf-8")

    written = build_section(draft.section, dry_run=False)

    commit_sha = None
    github_pushed = False
    if draft.push_github:
        if not github:
            raise GitHubError("GitHub is not configured (missing token or repo)")
        files = collect_section_build_outputs(draft.section)
        rel_md = md_path.relative_to(ROOT).as_posix()
        files[rel_md] = md_text
        message = f"Publish: {draft.title}"
        commit_sha = commit_files(github, message, files)
        github_pushed = True

    return PublishResult(
        slug=slug,
        markdown_path=md_path,
        written_paths=written,
        commit_sha=commit_sha,
        github_pushed=github_pushed,
    )
