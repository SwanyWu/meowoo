from __future__ import annotations

from datetime import date
from pathlib import Path

from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from admin.auth import LoginRequired, login, logout, require_auth
from admin.config import Settings, get_settings
from publisher.github_client import GitHubError
from publisher.publish import (
    PublishDraft,
    delete_post,
    list_manageable_posts,
    load_post_source,
    publish_post,
    update_post,
)

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
templates.env.globals["public_site_url"] = _settings.public_site_url

app.add_middleware(
    SessionMiddleware,
    secret_key=_settings.secret_key,
    https_only=_settings.session_https_only,
    same_site=_settings.session_same_site,
    domain=_settings.session_cookie_domain,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=list(_settings.cors_origins),
    allow_credentials=True,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)


@app.exception_handler(LoginRequired)
async def _login_required(_request: Request, _exc: LoginRequired) -> RedirectResponse:
    return RedirectResponse("/login", status_code=303)


def _form_fields(
    *,
    section: str,
    title: str,
    slug: str,
    post_date: str,
    excerpt: str,
    description: str,
    post_vibe: str,
    body: str,
) -> dict[str, str]:
    return {
        "section": section,
        "title": title,
        "slug": slug,
        "post_date": post_date,
        "excerpt": excerpt,
        "description": description,
        "post_vibe": post_vibe,
        "body": body,
    }


def _parse_draft_from_form(
    *,
    section: str,
    title: str,
    slug: str,
    post_date: str,
    excerpt: str,
    description: str,
    post_vibe: str,
    body: str,
    push_github: str,
    cfg: Settings,
) -> tuple[PublishDraft, dict[str, str] | None]:
    form = _form_fields(
        section=section,
        title=title,
        slug=slug,
        post_date=post_date,
        excerpt=excerpt,
        description=description,
        post_vibe=post_vibe,
        body=body,
    )
    wants_github = push_github == "on"
    if wants_github and not cfg.github_enabled:
        return (
            PublishDraft(
                section=section,
                title="",
                body="",
                excerpt="",
                post_date=date.today(),
                push_github=False,
            ),
            form,
        )

    try:
        parsed_date = date.fromisoformat(post_date)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid date") from exc

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
    return draft, None


def _success_message(result, draft: PublishDraft, *, verb: str) -> str:
    paths = ", ".join(p.relative_to(ROOT).as_posix() for p in result.written_paths)
    msg = f"{verb} {result.markdown_path.relative_to(ROOT)}. Built: {paths or '(unchanged HTML)'}."
    if result.github_pushed and result.commit_sha:
        msg += f" Pushed to GitHub ({result.commit_sha[:7]})."
    return msg


def _post_form_context(
    cfg: Settings,
    *,
    page_title: str,
    header_title: str,
    form_action: str,
    submit_label: str,
    edit_mode: bool = False,
    original_section: str | None = None,
    original_slug: str | None = None,
    form: dict | None = None,
    error: str | None = None,
    success: str | None = None,
) -> dict:
    return {
        "sections": cfg.publish_sections,
        "today": date.today().isoformat(),
        "github_enabled": cfg.github_enabled,
        "page_title": page_title,
        "header_title": header_title,
        "form_action": form_action,
        "submit_label": submit_label,
        "edit_mode": edit_mode,
        "original_section": original_section,
        "original_slug": original_slug,
        "form": form,
        "error": error,
        "success": success,
    }


def _assert_section(cfg: Settings, section: str) -> None:
    if section not in cfg.publish_sections:
        raise HTTPException(status_code=404, detail="Section not allowed")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/auth/status")
def auth_status(request: Request, cfg: Settings = Depends(settings)) -> dict:
    if not request.session.get("authenticated"):
        raise HTTPException(status_code=401, detail="Not authenticated")
    return {"authenticated": True, "sections": list(cfg.publish_sections)}


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
    posts = list_manageable_posts(cfg.publish_sections)
    return templates.TemplateResponse(
        request,
        "dashboard.html",
        {
            "sections": cfg.publish_sections,
            "github_enabled": cfg.github_enabled,
            "posts": posts,
        },
    )


@app.get("/admin/new", response_class=HTMLResponse)
def new_post_page(request: Request, cfg: Settings = Depends(settings)) -> HTMLResponse:
    require_auth(request)
    ctx = _post_form_context(
        cfg,
        page_title="New post",
        header_title="New post",
        form_action="/admin/publish",
        submit_label="Publish",
    )
    return templates.TemplateResponse(request, "post_form.html", ctx)


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
    _assert_section(cfg, section)

    draft, form = _parse_draft_from_form(
        section=section,
        title=title,
        slug=slug,
        post_date=post_date,
        excerpt=excerpt,
        description=description,
        post_vibe=post_vibe,
        body=body,
        push_github=push_github,
        cfg=cfg,
    )
    ctx = _post_form_context(
        cfg,
        page_title="New post",
        header_title="New post",
        form_action="/admin/publish",
        submit_label="Publish",
        form=form or _form_fields(
            section=section,
            title=title,
            slug=slug,
            post_date=post_date,
            excerpt=excerpt,
            description=description,
            post_vibe=post_vibe,
            body=body,
        ),
    )
    if form is not None:
        ctx["error"] = "GitHub push is checked but GITHUB_TOKEN is not set in .env."
        return templates.TemplateResponse(request, "post_form.html", ctx, status_code=400)

    try:
        result = publish_post(draft, cfg.github_config() if draft.push_github else None)
    except (GitHubError, ValueError) as exc:
        ctx["error"] = str(exc)
        return templates.TemplateResponse(request, "post_form.html", ctx, status_code=400)

    ctx["success"] = _success_message(result, draft, verb="Saved")
    return templates.TemplateResponse(request, "post_form.html", ctx)


@app.get("/admin/edit/{section}/{slug}", response_class=HTMLResponse)
def edit_post_page(
    request: Request,
    section: str,
    slug: str,
    cfg: Settings = Depends(settings),
) -> HTMLResponse:
    require_auth(request)
    _assert_section(cfg, section)
    try:
        src = load_post_source(section, slug)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    ctx = _post_form_context(
        cfg,
        page_title="Edit post",
        header_title="Edit post",
        form_action=f"/admin/edit/{section}/{slug}",
        submit_label="Save changes",
        edit_mode=True,
        original_section=section,
        original_slug=slug,
        form={
            "section": src.section,
            "title": src.title,
            "slug": src.slug,
            "post_date": src.post_date.isoformat(),
            "excerpt": src.excerpt,
            "description": src.description or "",
            "post_vibe": src.post_vibe or "",
            "body": src.body,
        },
    )
    return templates.TemplateResponse(request, "post_form.html", ctx)


@app.post("/admin/edit/{section}/{slug}", response_class=HTMLResponse)
def edit_post_submit(
    request: Request,
    section: str,
    slug: str,
    original_section: str = Form(...),
    original_slug: str = Form(...),
    title: str = Form(...),
    new_slug: str = Form("", alias="slug"),
    post_date: str = Form(...),
    excerpt: str = Form(...),
    description: str = Form(""),
    post_vibe: str = Form(""),
    body: str = Form(...),
    push_github: str = Form(""),
    cfg: Settings = Depends(settings),
) -> HTMLResponse:
    require_auth(request)
    _assert_section(cfg, section)
    if section != original_section or slug != original_slug:
        raise HTTPException(status_code=400, detail="URL does not match post identity")

    draft, form = _parse_draft_from_form(
        section=original_section,
        title=title,
        slug=new_slug,
        post_date=post_date,
        excerpt=excerpt,
        description=description,
        post_vibe=post_vibe,
        body=body,
        push_github=push_github,
        cfg=cfg,
    )
    ctx = _post_form_context(
        cfg,
        page_title="Edit post",
        header_title="Edit post",
        form_action=f"/admin/edit/{section}/{slug}",
        submit_label="Save changes",
        edit_mode=True,
        original_section=original_section,
        original_slug=original_slug,
        form=form
        or _form_fields(
            section=original_section,
            title=title,
            slug=new_slug,
            post_date=post_date,
            excerpt=excerpt,
            description=description,
            post_vibe=post_vibe,
            body=body,
        ),
    )
    if form is not None:
        ctx["error"] = "GitHub push is checked but GITHUB_TOKEN is not set in .env."
        return templates.TemplateResponse(request, "post_form.html", ctx, status_code=400)

    try:
        existing = load_post_source(original_section, original_slug)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    draft.page_class = existing.page_class
    draft.subtitle = existing.subtitle
    draft.tags = existing.tags

    try:
        result = update_post(
            original_section,
            original_slug,
            draft,
            cfg.github_config() if draft.push_github else None,
        )
    except (GitHubError, ValueError) as exc:
        ctx["error"] = str(exc)
        return templates.TemplateResponse(request, "post_form.html", ctx, status_code=400)

    if result.slug != original_slug:
        return RedirectResponse(f"/admin/edit/{original_section}/{result.slug}", status_code=303)

    ctx["original_slug"] = result.slug
    ctx["success"] = _success_message(result, draft, verb="Updated")
    return templates.TemplateResponse(request, "post_form.html", ctx)


@app.post("/admin/delete/{section}/{slug}")
def delete_post_submit(
    request: Request,
    section: str,
    slug: str,
    push_github: str = Form(""),
    cfg: Settings = Depends(settings),
) -> RedirectResponse:
    require_auth(request)
    _assert_section(cfg, section)
    wants_github = push_github == "on"
    if wants_github and not cfg.github_enabled:
        raise HTTPException(status_code=400, detail="GITHUB_TOKEN is not set")

    try:
        delete_post(
            section,
            slug,
            push_github=wants_github,
            github=cfg.github_config() if wants_github else None,
        )
    except (GitHubError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return RedirectResponse("/admin", status_code=303)
