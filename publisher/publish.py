"""Write locally and push built site files to GitHub."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path

from publisher.build import (
    CONTENT_DIR,
    ROOT,
    build_section,
    collect_section_build_outputs,
    discover_posts,
    load_sections,
    parse_frontmatter,
    parse_date,
)
from publisher.content import compose_post_markdown, slugify
from publisher.github_client import GitHubConfig, GitHubError, commit_files


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
class PostSource:
    section: str
    slug: str
    title: str
    body: str
    excerpt: str
    post_date: date
    description: str | None
    post_vibe: str | None
    page_class: str | None
    subtitle: str | None
    tags: list[str] | None


@dataclass
class PublishResult:
    slug: str
    markdown_path: Path
    written_paths: list[Path]
    commit_sha: str | None
    github_pushed: bool


@dataclass
class DeleteResult:
    slug: str
    written_paths: list[Path]
    commit_sha: str | None
    github_pushed: bool


def post_markdown_path(section: str, slug: str) -> Path:
    return CONTENT_DIR / section / f"{slug}.md"


def post_html_path(section: str, slug: str) -> Path:
    sub = load_sections()[section]["post_subdirectory"]
    return ROOT / sub / f"{slug}.html"


def list_manageable_posts(sections: tuple[str, ...]) -> list[PostSource]:
    posts: list[PostSource] = []
    for section in sections:
        if section not in load_sections():
            continue
        for post in discover_posts(section):
            src = load_post_source(section, post.slug)
            posts.append(src)
    posts.sort(key=lambda p: p.post_date, reverse=True)
    return posts


def load_post_source(section: str, slug: str) -> PostSource:
    path = post_markdown_path(section, slug)
    if not path.is_file():
        raise ValueError(f"Post not found: {section}/{slug}")

    raw = path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(raw)
    return PostSource(
        section=section,
        slug=slug,
        title=meta["title"],
        body=body.rstrip("\n"),
        excerpt=meta.get("excerpt", ""),
        post_date=parse_date(meta["date"]),
        description=meta.get("description"),
        post_vibe=meta.get("post_vibe"),
        page_class=meta.get("page_class"),
        subtitle=meta.get("subtitle"),
        tags=meta.get("tags"),
    )


def _resolve_slug(draft: PublishDraft) -> str:
    slug = (draft.slug or slugify(draft.title)).strip()
    if not slug:
        raise ValueError("Could not derive slug from title")
    return slug


def _compose_md(draft: PublishDraft) -> str:
    return compose_post_markdown(
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


def _remove_local_post_files(section: str, slug: str) -> list[Path]:
    removed: list[Path] = []
    md = post_markdown_path(section, slug)
    html = post_html_path(section, slug)
    if md.is_file():
        md.unlink()
        removed.append(md)
    if html.is_file():
        html.unlink()
        removed.append(html)
    return removed


def _github_push_section(
    github: GitHubConfig,
    section: str,
    message: str,
    md_path: Path,
    md_text: str,
    delete_paths: list[str],
) -> str:
    files = collect_section_build_outputs(section)
    rel_md = md_path.relative_to(ROOT).as_posix()
    files[rel_md] = md_text
    return commit_files(github, message, files, delete_paths=delete_paths)


def publish_post(draft: PublishDraft, github: GitHubConfig | None) -> PublishResult:
    sections = load_sections()
    if draft.section not in sections:
        raise ValueError(f"Unknown section: {draft.section}")

    slug = _resolve_slug(draft)
    md_text = _compose_md(draft)
    md_path = post_markdown_path(draft.section, slug)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(md_text, encoding="utf-8")

    written = build_section(draft.section, dry_run=False)

    commit_sha = None
    github_pushed = False
    if draft.push_github:
        if not github:
            raise GitHubError("GitHub is not configured (missing token or repo)")
        commit_sha = _github_push_section(
            github, draft.section, f"Publish: {draft.title}", md_path, md_text, []
        )
        github_pushed = True

    return PublishResult(
        slug=slug,
        markdown_path=md_path,
        written_paths=written,
        commit_sha=commit_sha,
        github_pushed=github_pushed,
    )


def update_post(
    original_section: str,
    original_slug: str,
    draft: PublishDraft,
    github: GitHubConfig | None,
) -> PublishResult:
    sections = load_sections()
    if draft.section not in sections:
        raise ValueError(f"Unknown section: {draft.section}")
    if original_section not in sections:
        raise ValueError(f"Unknown section: {original_section}")
    if original_section != draft.section:
        raise ValueError("Moving posts between sections is not supported")

    if not post_markdown_path(original_section, original_slug).is_file():
        raise ValueError(f"Post not found: {original_section}/{original_slug}")

    slug = _resolve_slug(draft)
    md_text = _compose_md(draft)
    md_path = post_markdown_path(draft.section, slug)

    delete_paths: list[str] = []
    if original_slug != slug:
        for path in _remove_local_post_files(original_section, original_slug):
            delete_paths.append(path.relative_to(ROOT).as_posix())

    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(md_text, encoding="utf-8")

    written = build_section(draft.section, dry_run=False)

    commit_sha = None
    github_pushed = False
    if draft.push_github:
        if not github:
            raise GitHubError("GitHub is not configured (missing token or repo)")
        commit_sha = _github_push_section(
            github,
            draft.section,
            f"Update: {draft.title}",
            md_path,
            md_text,
            delete_paths,
        )
        github_pushed = True

    return PublishResult(
        slug=slug,
        markdown_path=md_path,
        written_paths=written,
        commit_sha=commit_sha,
        github_pushed=github_pushed,
    )


def delete_post(
    section: str,
    slug: str,
    *,
    push_github: bool,
    github: GitHubConfig | None,
) -> DeleteResult:
    sections = load_sections()
    if section not in sections:
        raise ValueError(f"Unknown section: {section}")

    md = post_markdown_path(section, slug)
    if not md.is_file():
        raise ValueError(f"Post not found: {section}/{slug}")

    delete_paths = [p.relative_to(ROOT).as_posix() for p in _remove_local_post_files(section, slug)]
    written = build_section(section, dry_run=False)

    commit_sha = None
    github_pushed = False
    if push_github:
        if not github:
            raise GitHubError("GitHub is not configured (missing token or repo)")
        files = collect_section_build_outputs(section)
        commit_sha = commit_files(
            github,
            f"Delete: {section}/{slug}",
            files,
            delete_paths=delete_paths,
        )
        github_pushed = True

    return DeleteResult(
        slug=slug,
        written_paths=written,
        commit_sha=commit_sha,
        github_pushed=github_pushed,
    )
