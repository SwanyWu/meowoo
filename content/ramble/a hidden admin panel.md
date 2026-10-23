---
title: Much is done
date: '2026-10-23'
excerpt: From Markdown sources to a Render publisher—and an author bar only I see.
---

Today the site changed from hand-editing HTML to a small publishing pipeline.

**Phase 1 — Markdown → HTML**
Ramble (and later looksie and nom) use Markdown under `content/`. A Python build step turns those files into the static HTML GitHub Pages serves. The Markdown is the source of truth; HTML is rebuilt and committed.

**Phase 2 — Publisher admin**  
There is a password-protected publisher app on Render (custom hostname on my domain). It creates or updates Markdown, runs the build, and can push a single commit to GitHub. Secrets live in the host environment, not in the repo. (I did this to practice FastAPI)

**Local → cloud**
The public site stays on GitHub Pages. The publisher is a separate HTTPS app. When I am logged in, a small script on public pages can show edit links; everyone else sees normal pages.

Looksie posts can include spoiler-gated diagrams; nom has an interactive widget—both wired into the same build. The web UI is still easiest for ramble.
