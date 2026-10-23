from __future__ import annotations

from datetime import date
from pathlib import Path

from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from admin.auth import LoginRequired, login, logout, require_auth
from admin.config import Settings, get_settings
from publisher.github_client import GitHubError
from publisher.publish import PublishDraft, publish_post

ROOT = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(ROOT / "templates" / "admin"))

app = FastAPI(title="meowoo publisher", docs_url=None, redoc_url=None)
app.mount("/static", StaticFiles(directory=str(ROOT / "admin" / "static")), name="static")


@app.on_event("startup")
def _check_settings() -> None:
    get_settings()


def settings() -> Settings:
    return get_settings()


_settings = get_settings()
app.add_middleware(SessionMiddleware, secret_key=_settings.secret_key, https_only=False)


@app.exception_handler(LoginRequired)
async def _login_required(_request: Request, _exc: LoginRequired) -> RedirectResponse:
    return RedirectResponse("/login", status_code=303)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request) -> HTMLResponse:
    if request.session.get("authenticated"):
        return RedirectResponse("/admin", status_code=303)
    return templates.TemplateResponse(
        request,
        "login.html",
        {"error": None},
    )


@app.post("/login", response_class=HTMLResponse)
def login_submit(
    request: Request,
    password: str = Form(...),
    cfg: Settings = Depends(settings),
):
    try:
        login(request, password, cfg.admin_password)
    except HTTPException:
        return templates.TemplateResponse(
            request,
            "login.html",
            {"error": "Wrong password."},
            status_code=401,
        )
    return RedirectResponse("/admin", status_code=303)


@app.post("/logout")
def logout_submit(request: Request) -> RedirectResponse:
    logout(request)
    return RedirectResponse("/login", status_code=303)


@app.get("/admin", response_class=HTMLResponse)
def admin_home(request: Request, cfg: Settings = Depends(settings)) -> HTMLResponse:
    require_auth(request)
    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "sections": cfg.publish_sections,
            "github_enabled": cfg.github_enabled,
        },
    )


@app.get("/admin/new", response_class=HTMLResponse)
def new_post_page(request: Request, cfg: Settings = Depends(settings)) -> HTMLResponse:
    require_auth(request)
    return templates.TemplateResponse(
        request,
        "new_post.html",
        {
            "sections": cfg.publish_sections,
            "today": date.today().isoformat(),
            "github_enabled": cfg.github_enabled,
            "error": None,
            "success": None,
        },
    )


@app.post("/admin/publish", response_class=HTMLResponse)
def publish_form(
    request: Request,
    section: str = Form(...),
    title: str = Form(...),
    slug: str = Form(""),
    post_date: str = Form(...),
    excerpt: str = Form(...),
    description: str = Form(""),
    post_vibe: str = Form(""),
    body: str = Form(...),
    push_github: str = Form(""),
    cfg: Settings = Depends(settings),
) -> HTMLResponse:
    require_auth(request)

    if section not in cfg.publish_sections:
        raise HTTPException(status_code=400, detail="Section not allowed")

    try:
        parsed_date = date.fromisoformat(post_date)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid date") from exc

    wants_github = push_github == "on"
    if wants_github and not cfg.github_enabled:
        ctx = {
            "sections": cfg.publish_sections,
            "today": date.today().isoformat(),
            "github_enabled": cfg.github_enabled,
            "error": "GitHub push is checked but GITHUB_TOKEN is not set in .env.",
            "success": None,
            "form": {
                "section": section,
                "title": title,
                "slug": slug,
                "post_date": post_date,
                "excerpt": excerpt,
                "description": description,
                "post_vibe": post_vibe,
                "body": body,
            },
        }
        return templates.TemplateResponse(request, "new_post.html", ctx, status_code=400)

    draft = PublishDraft(
        section=section,
        title=title.strip(),
        body=body,
        excerpt=excerpt.strip(),
        post_date=parsed_date,
        slug=slug.strip() or None,
        description=description.strip() or None,
        post_vibe=post_vibe.strip() or None,
        push_github=wants_github,
    )

    ctx = {
        "sections": cfg.publish_sections,
        "today": date.today().isoformat(),
        "github_enabled": cfg.github_enabled,
        "error": None,
        "success": None,
        "form": {
            "section": section,
            "title": title,
            "slug": slug,
            "post_date": post_date,
            "excerpt": excerpt,
            "description": description,
            "post_vibe": post_vibe,
            "body": body,
        },
    }

    try:
        result = publish_post(draft, cfg.github_config() if draft.push_github else None)
    except (GitHubError, ValueError) as exc:
        ctx["error"] = str(exc)
        return templates.TemplateResponse(request, "new_post.html", ctx, status_code=400)

    paths = ", ".join(p.relative_to(ROOT).as_posix() for p in result.written_paths)
    msg = f"Saved {result.markdown_path.relative_to(ROOT)}. Built: {paths or '(unchanged HTML)'}."
    if result.github_pushed and result.commit_sha:
        msg += f" Pushed to GitHub ({result.commit_sha[:7]})."
    ctx["success"] = msg
    return templates.TemplateResponse(request, "new_post.html", ctx)
