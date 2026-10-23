"""Compose Markdown source files from editor input."""

from __future__ import annotations

import re
from datetime import date

import yaml


def slugify(title: str) -> str:
    s = title.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s, flags=re.UNICODE)
    s = re.sub(r"[\s_]+", "-", s)
    return s.strip("-") or "post"


def compose_post_markdown(
    *,
    title: str,
    post_date: date,
    excerpt: str,
    body: str,
    description: str | None = None,
    post_vibe: str | None = None,
    page_class: str | None = None,
    subtitle: str | None = None,
    tags: list[str] | None = None,
) -> str:
    meta: dict = {
        "title": title,
        "date": post_date.isoformat(),
        "excerpt": excerpt,
    }
    if description:
        meta["description"] = description
    if post_vibe:
        meta["post_vibe"] = post_vibe
    if page_class:
        meta["page_class"] = page_class
    if subtitle:
        meta["subtitle"] = subtitle
    if tags:
        meta["tags"] = tags

    front = yaml.safe_dump(meta, sort_keys=False, allow_unicode=True).strip()
    body = body.strip() + "\n"
    return f"---\n{front}\n---\n\n{body}"
