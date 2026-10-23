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

## Deploy admin on Render

The public site stays on **GitHub Pages**. Render runs only the **publisher admin** (private URL or `admin.meowoo.me`).

**On Render:**

1. [dashboard.render.com](https://dashboard.render.com) → **Sign in with GitHub**.
2. **New +** → **Web Service** → connect **`SwanyWu/meowoo`** (or use **Blueprint** if `render.yaml` is on `main`).
3. Settings (if not using Blueprint):
   - **Runtime:** Python 3
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `uvicorn admin.main:app --host 0.0.0.0 --port $PORT`
   - **Health check path:** `/health`
4. **Environment** → add secrets (never commit these):

   | Key | Value |
   |-----|--------|
   | `ADMIN_PASSWORD` | Strong login password |
   | `SECRET_KEY` | Long random string |
   | `GITHUB_TOKEN` | Fine-grained PAT, **Contents: Read and write** on `meowoo` |
   | `GITHUB_REPO` | `SwanyWu/meowoo` |
   | `GITHUB_BRANCH` | `main` |
   | `PUBLISH_SECTIONS` | `ramble` (or `ramble,looksie,nom` when admin supports them) |

   Render sets `RENDER=true`, which turns on **HTTPS-only session cookies**.

5. **Create Web Service** → wait for deploy → open the `*.onrender.com` URL → `/login`.

6. **Custom domain (optional):** Render service → **Settings → Custom Domains** → add `admin.meowoo.me`. At your DNS host, add a **CNAME** `admin` → the hostname Render gives you (not the same record as GitHub Pages for the root site).

**Important on Render:** The server disk is ephemeral. Always publish with **Push to GitHub** checked so commits land on `main`; otherwise changes disappear on restart.

Free tier services **spin down** when idle; the first visit after sleep may take ~30s.
