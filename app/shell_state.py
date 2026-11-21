"""Shell-level helpers: global search resolution across pages.

Ported from the Reflex app's ShellState.search_submit.
"""
from nicegui import ui

PAGES = [
    {"label": "Ecommerce dashboard", "href": "/", "keywords": "dashboard ecommerce"},
    {"label": "Menu", "href": "/menu", "keywords": "menu"},
    {"label": "Files", "href": "/files", "keywords": "files"},
    {"label": "GitHub Sync", "href": "/github", "keywords": "github sync"},
    {"label": "Authentication / Account", "href": "/auth", "keywords": "authentication account auth signin login"},
]


def resolve_search(query: str) -> None:
    """Navigate to the first page matching the query, or notify if nothing matches."""
    q = (query or "").strip().lower()
    if not q:
        return
    for page in PAGES:
        haystack = f"{page['label']} {page['keywords']}".lower()
        if q in haystack or any(word in haystack for word in q.split()):
            ui.navigate.to(page["href"])
            return
    ui.notify(
        "Search for Dashboard, Menu, Files, GitHub Sync, or Authentication.",
        type="info",
    )