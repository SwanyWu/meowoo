"""Build static HTML from content/{section}/*.md."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path(__file__).resolve().parent.parent
CONTENT_DIR = ROOT / "content"
DATA_DIR = ROOT / "data"
TEMPLATES_DIR = ROOT / "templates"

INTERACTIVE_WIDGETS: dict[str, dict[str, str]] = {
    "dumpling-assembly-line": {
        "partial": "interactive/dumpling-assembly-line.html.j2",
        "script": "js/dumpling-assembly-line.js",
    },
}


@dataclass
class SpoilerChart:
    spoiler_warning: str
    title: str
    lead: str
    mermaid: str


@dataclass
class Post:
    section: str
    slug: str
    title: str
    date: date
    excerpt: str
    description: str | None
    body_html: str
    post_vibe: str | None
    page_class: str
    meta_tags: list[str]
    subtitle: str | None
    lead: str | None = None
    interactive: str | None = None
    chart: SpoilerChart | None = None

    @property
    def interactive_partial(self) -> str | None:
        if not self.interactive:
            return None
        widget = INTERACTIVE_WIDGETS.get(self.interactive)
        if not widget:
            raise ValueError(f"Unknown interactive widget: {self.interactive}")
        return widget["partial"]

    @property
    def interactive_script(self) -> str | None:
        if not self.interactive:
            return None
        widget = INTERACTIVE_WIDGETS.get(self.interactive)
        if not widget:
            return None
        return widget["script"]

    @property
    def date_display(self) -> str:
        d = self.date.day
        return f"{d} {self.date.strftime('%b %Y')}"

    @property
    def date_iso(self) -> str:
        return self.date.isoformat()

    @property
    def output_path(self) -> Path:
        section_cfg = load_sections()[self.section]
        sub = section_cfg["post_subdirectory"]
        return ROOT / sub / f"{self.slug}.html"

    @property
    def card_href(self) -> str:
        section_cfg = load_sections()[self.section]
        sub = section_cfg["post_subdirectory"]
        return f"{sub}/{self.slug}.html"


def load_sections() -> dict:
    with (DATA_DIR / "sections.yaml").open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def parse_frontmatter(raw: str) -> tuple[dict, str]:
    if not raw.startswith("---"):
        return {}, raw
    match = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n(.*)$", raw, re.DOTALL)
    if not match:
        return {}, raw
    meta = yaml.safe_load(match.group(1)) or {}
    body = match.group(2)
    return meta, body


def parse_date(value) -> date:
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    return date.fromisoformat(str(value))


def markdown_to_html(body: str) -> str:
    return markdown.markdown(
        body,
        extensions=["extra", "smarty"],
        output_format="html5",
    )


def _load_chart(meta: dict) -> SpoilerChart | None:
    raw = meta.get("chart")
    if not raw:
        return None
    mermaid = raw.get("mermaid", "").strip()
    if not mermaid:
        return None
    return SpoilerChart(
        spoiler_warning=raw.get("spoiler_warning", "Spoilers ahead."),
        title=raw.get("title", "Chart"),
        lead=raw.get("lead", ""),
        mermaid=mermaid,
    )


def load_post(path: Path, section: str) -> Post:
    raw = path.read_text(encoding="utf-8")
    meta, body = parse_frontmatter(raw)
    slug = path.stem
    title = meta["title"]
    return Post(
        section=section,
        slug=slug,
        title=title,
        date=parse_date(meta["date"]),
        excerpt=meta.get("excerpt", ""),
        description=meta.get("description"),
        body_html=markdown_to_html(body),
        post_vibe=meta.get("post_vibe"),
        page_class=meta.get("page_class", "page--post"),
        meta_tags=meta.get("tags") or [],
        subtitle=meta.get("subtitle"),
        lead=meta.get("lead"),
        interactive=meta.get("interactive"),
        chart=_load_chart(meta),
    )


def discover_posts(section: str) -> list[Post]:
    section_dir = CONTENT_DIR / section
    if not section_dir.is_dir():
        return []
    posts = [load_post(p, section) for p in sorted(section_dir.glob("*.md"))]
    posts.sort(key=lambda p: p.date, reverse=True)
    return posts


def jinja_env() -> Environment:
    return Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        autoescape=select_autoescape(["html", "xml"]),
    )


def render_post(post: Post) -> str:
    sections = load_sections()
    cfg = sections[post.section]
    env = jinja_env()
    tpl = env.get_template("post.html.j2")
    meta_description = post.description or f"{post.title} · {post.section} · meowoo.me"
    return tpl.render(
        post=post,
        section=cfg,
        section_id=post.section,
        meta_description=meta_description,
        assets_prefix="../",
        root_prefix="../",
    )


def render_section_index(section: str, posts: list[Post]) -> str:
    sections = load_sections()
    cfg = sections[section]
    env = jinja_env()
    tpl = env.get_template("section_index.html.j2")
    return tpl.render(
        section=cfg,
        section_id=section,
        posts=posts,
        meta_description=cfg["meta_description"],
        assets_prefix="",
        root_prefix="",
    )


def write_if_changed(path: Path, content: str) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return False
    path.write_text(content, encoding="utf-8")
    return True


def collect_section_build_outputs(section: str) -> dict[str, str]:
    """Render all post pages and section index for GitHub commit."""
    sections = load_sections()
    if section not in sections:
        raise ValueError(f"Unknown section: {section}")

    outputs: dict[str, str] = {}
    posts = discover_posts(section)
    for post in posts:
        rel = post.output_path.relative_to(ROOT).as_posix()
        outputs[rel] = render_post(post)

    index_path = ROOT / sections[section]["index_output"]
    outputs[index_path.relative_to(ROOT).as_posix()] = render_section_index(section, posts)
    return outputs


def build_section(section: str, dry_run: bool = False) -> list[Path]:
    sections = load_sections()
    if section not in sections:
        raise ValueError(f"Unknown section: {section}")

    changed: list[Path] = []
    posts = discover_posts(section)

    for post in posts:
        html = render_post(post)
        out = post.output_path
        if dry_run:
            print(f"Would write {out.relative_to(ROOT)}")
        elif write_if_changed(out, html):
            changed.append(out)

    index_html = render_section_index(section, posts)
    index_path = ROOT / sections[section]["index_output"]
    if dry_run:
        print(f"Would write {index_path.relative_to(ROOT)}")
    elif write_if_changed(index_path, index_html):
        changed.append(index_path)

    return changed


def build_all(dry_run: bool = False) -> list[Path]:
    sections = load_sections()
    changed: list[Path] = []
    for section in sections:
        if not (CONTENT_DIR / section).is_dir():
            continue
        changed.extend(build_section(section, dry_run=dry_run))
    return changed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build meowoo.me HTML from Markdown.")
    parser.add_argument(
        "--section",
        "-s",
        help="Build only this section (e.g. ramble)",
    )
    parser.add_argument(
        "--all",
        "-a",
        action="store_true",
        help="Build all sections that have content/",
    )
    parser.add_argument(
        "--dry-run",
        "-n",
        action="store_true",
        help="Print paths that would be written",
    )
    args = parser.parse_args(argv)

    if not args.all and not args.section:
        parser.error("Use --all or --section")

    if args.section:
        changed = build_section(args.section, dry_run=args.dry_run)
    else:
        changed = build_all(dry_run=args.dry_run)

    if args.dry_run:
        return 0

    if changed:
        for path in changed:
            print(f"Wrote {path.relative_to(ROOT)}")
    else:
        print("No changes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
