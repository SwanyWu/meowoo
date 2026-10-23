from __future__ import annotations

from fastapi import HTTPException, Request


class LoginRequired(Exception):
    pass


def login(request: Request, password: str, expected: str) -> None:
    if password != expected:
        raise HTTPException(status_code=401, detail="Invalid password")
    request.session["authenticated"] = True


def logout(request: Request) -> None:
    request.session.clear()


def require_auth(request: Request) -> None:
    if not request.session.get("authenticated"):
        raise LoginRequired()
