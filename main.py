"""TailAdmin (AdministrationRP) — NiceGUI entry point.

Replaces the original Reflex app. Routes:
  /          Dashboard (Ecommerce)
  /menu      Menu hierarchy management
  /files     Private file manager (auth-guarded)
  /github    GitHub Sync (feature unavailable)
  /auth      Sign in / sign up
  /account   Account profile (auth-guarded)

Run locally:  uv run python main.py
"""
import os

from nicegui import app, ui

from app import (
    account_page,
    dashboard_page,
    files_page,
    github_page,
    menu_page,
)
from app.db import init_db
from app.theme import GLOBAL_CSS


@app.on_startup
def _startup():
    init_db()


@ui.page("/")
def index():
    _setup("Dashboard — TailAdmin")
    dashboard_page.build()


@ui.page("/menu")
def menu_route():
    _setup("Menu — TailAdmin")
    menu_page.build()


@ui.page("/files")
def files_route():
    _setup("Files — TailAdmin")
    files_page.build()


@ui.page("/github")
def github_route():
    _setup("GitHub Sync — TailAdmin")
    github_page.build()


@ui.page("/auth")
def auth_route():
    _setup("Authentication — TailAdmin")
    account_page.auth_build()


@ui.page("/account")
def account_route():
    _setup("Account — TailAdmin")
    account_page.account_build()


def _setup(title: str):
    ui.add_css(GLOBAL_CSS)
    ui.colors(primary="#465FFF")
    ui.add_head_html(
        f"<title>{title}</title>"
        '<link rel="preconnect" href="https://fonts.googleapis.com">'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
        '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">'
    )


if __name__ in {"__main__", "__mp_main__"}:
    in_container = bool(os.environ.get("PORT")) or os.path.exists("/.dockerenv")
    port = int(os.environ.get("PORT", "8080"))
    ui.run(
        title="TailAdmin",
        favicon="🧩",
        host="0.0.0.0",
        port=port,
        reload=not in_container,
        show=not in_container,
        storage_secret=os.environ.get("STORAGE_SECRET", "tailadmin-dev-secret-change-me"),
    )