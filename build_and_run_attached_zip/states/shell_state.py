import reflex as rx
from typing import TypedDict, Any


class PageLink(TypedDict):
    label: str
    href: str
    icon: str


class ShellState(rx.State):
    mobile_open: bool = False
    dashboard_open: bool = True
    search: str = ""
    pages: list[PageLink] = [
        {
            "label": "Ecommerce dashboard",
            "href": "/",
            "icon": "layout-dashboard",
        },
        {"label": "Menu", "href": "/menu", "icon": "list-tree"},
        {"label": "Files", "href": "/files", "icon": "folder"},
        {"label": "GitHub Sync", "href": "/github", "icon": "github"},
        {
            "label": "Authentication / Account",
            "href": "/auth",
            "icon": "lock-keyhole",
        },
    ]

    @rx.event
    def search_submit(self, form_data: dict[str, Any]):
        query = str(form_data.get("search", "")).strip().lower()
        matches = [
            page for page in self.pages if query in page["label"].lower()
        ]
        if query and matches:
            self.search = ""
            self.mobile_open = False
            return rx.redirect(matches[0]["href"])
        return rx.toast(
            "Search for Dashboard, Menu, Files, GitHub Sync, or Authentication."
        )

    @rx.event
    def toggle_mobile(self):
        self.mobile_open = not self.mobile_open

    @rx.event
    def close_mobile(self):
        self.mobile_open = False
        self.search = ""

    @rx.event
    def toggle_dashboard(self):
        self.dashboard_open = not self.dashboard_open
