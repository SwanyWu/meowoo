# meowoo.me

Personal site (GitHub Pages) with a local **publisher admin** for Markdown ramble posts.

## Setup (once)

```bash
cd /Users/huiyaowu/meowoo
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Edit `.env`:

- `ADMIN_PASSWORD` — admin UI login
- `SECRET_KEY` — session signing (long random string)
- `GITHUB_TOKEN` — optional; required to push from the admin

## Run the admin

```bash
cd /Users/huiyaowu/meowoo
source .venv/bin/activate
uvicorn admin.main:app --reload --host 127.0.0.1 --port 8000
```

Open [http://127.0.0.1:8000/login](http://127.0.0.1:8000/login).

- **Dashboard** — list posts, edit, delete
- **New post** — write Markdown, build HTML, optionally push to GitHub in one commit

## Build from the CLI

```bash
source .venv/bin/activate
python -m publisher.build --section ramble
python -m publisher.build --section looksie
python -m publisher.build --section nom
python -m publisher.build --all
```

## Preview static site locally

```bash
cd /Users/huiyaowu/meowoo
python3 -m http.server 8080
```

Open [http://127.0.0.1:8080/](http://127.0.0.1:8080/).

## Content layout

- **Source:** `content/ramble/*.md`, `content/looksie/*.md`, `content/nom/*.md`
- **Generated:** section HTML under `ramble/`, `looksie/`, `nom/`, plus each section index
- Commit both source and HTML when publishing via git; the admin can push both via the GitHub API when `GITHUB_TOKEN` is set.

Looksie posts can include a `chart:` block in frontmatter (spoiler-gated Mermaid). Nom posts can set `interactive: dumpling-assembly-line` (widget partial + `js/dumpling-assembly-line.js`).

The admin UI is still **ramble-only**; edit looksie/nom Markdown by hand or extend `PUBLISH_SECTIONS` later.
