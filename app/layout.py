"""Shell layout: sidebar navigation + top header + hosting/footer sections.

Ported from the Reflex app's shell.py, hosting_footer.py, footer_links.py.
"""
from nicegui import ui

from . import session
from .hosting_service import ResourceUsage, collect_metrics, initial_resources


def _nav_link(label: str, icon: str, href: str, active: bool) -> None:
    cls = "ta-nav-item active" if active else "ta-nav-item"
    with ui.link("", href).classes(cls) as link:
        ui.icon(icon).classes("text-lg")
        ui.label(label)


def _sidebar(active: str) -> None:
    with ui.left_drawer(value=True).classes("w-64").style(
        "background: var(--ta-bg); border-right: 1px solid var(--ta-border)"
    ) as drawer:
        # Brand
        with ui.link("/", "").classes(
            "flex items-center gap-3 px-6"
        ).style("height: 5rem"):
            with ui.element("div").classes(
                "flex items-center justify-center rounded-xl"
            ).style(
                "width:2.5rem;height:2.5rem;background:var(--ta-primary);color:#fff"
            ):
                ui.icon("bar_chart").classes("text-xl text-white")
            ui.label("TailAdmin").classes("text-2xl font-bold tracking-tight").style(
                "color: var(--ta-text)"
            )
        # Nav
        with ui.column().classes("w-full px-4 py-7 gap-1 overflow-y-auto"):
            ui.label("MENU").classes(
                "mb-2 px-3 text-xs font-medium tracking-wider"
            ).style("color: var(--ta-muted-2)")

            # Dashboard (expandable)
            with ui.element("div").classes("w-full"):
                dashboard_open = {"v": True}

                def toggle_dashboard():
                    dashboard_open["v"] = not dashboard_open["v"]
                    children.set_visibility(dashboard_open["v"])
                    chevron.name = "expand_more" if dashboard_open["v"] else "chevron_right"

                with ui.row().classes("items-center w-full no-wrap"):
                    btn = ui.button(on_click=toggle_dashboard).props("flat dense no-caps").classes(
                        "ta-nav-item flex-grow"
                    )
                    with btn:
                        with ui.row().classes("items-center gap-3"):
                            ui.icon("dashboard").classes("text-lg")
                            ui.label("Dashboard")
                        chevron = ui.icon("expand_more").classes("text-base ml-auto").style(
                            "color: var(--ta-muted-2)"
                        )
                with ui.column().classes("w-full gap-1") as children:
                    with ui.link("Ecommerce", "/").classes(
                        "ta-nav-child active" if active == "Ecommerce" else "ta-nav-child"
                    ):
                        pass

            _nav_link("Menu", "list_tree", "/menu", active == "Menu")
            _nav_link("Files", "folder", "/files", active == "Files")
            _nav_link("GitHub Sync", "code", "/github", active == "GitHub Sync")

            ui.label("OTHERS").classes(
                "mt-8 mb-2 px-3 text-xs font-medium tracking-wider"
            ).style("color: var(--ta-muted-2)")
            _nav_link("Authentication", "lock", "/auth", active == "Authentication")

        # Sidebar footer note
        with ui.row().classes(
            "mx-5 mb-6 mt-auto gap-2 shrink-0"
        ).style("border-top:1px solid var(--ta-border); padding-top:1.25rem"):
            ui.icon("info").classes("text-base").style("color: var(--ta-muted-2)")
            ui.label("Sample dashboard · Session-only menu").classes(
                "text-xs leading-5"
            ).style("color: var(--ta-muted-2)")

    return drawer


def _header(drawer) -> None:
    with ui.header().classes("items-center justify-between px-4 lg:px-7").style(
        "background:#fff; border-bottom:1px solid var(--ta-border); height:5rem"
    ):
        with ui.row().classes("items-center gap-4 w-full no-wrap"):
            ui.button(icon="menu", on_click=lambda: drawer.toggle()).props(
                "flat dense round"
            ).style("color: var(--ta-text)")

            # Search
            search = ui.input(placeholder="Search or type command...").props(
                "outlined dense"
            ).classes("w-full").style("max-width:420px")
            with search.add_slot("append"):
                ui.button(icon="arrow_forward", on_click=lambda: _search(search)).props(
                    "flat dense round"
                ).style("color: var(--ta-muted)")

            # Auth chip
            with ui.row().classes("items-center gap-2 ml-auto no-wrap"):
                authenticated = session.is_authenticated()
                href = "/account" if authenticated else "/auth"
                label = "My account" if authenticated else "Sign in"
                with ui.link(href).classes(
                    "ta-btn"
                ).style("padding:.5rem 1rem; height:2.5rem"):
                    ui.icon("lock").classes("text-base")
                    ui.label(label).classes("hidden sm:inline")


def _search(search) -> None:
    from .shell_state import resolve_search

    resolve_search(search.value or "")
    search.set_value("")


def page_title(title: str, description: str) -> None:
    with ui.row().classes("items-center justify-between w-full mb-6 no-wrap"):
        with ui.column().classes("gap-1"):
            ui.label(title).classes("ta-page-title")
            if description:
                ui.label(description).classes("text-sm").style("color: var(--ta-muted)")
        with ui.row().classes("hidden sm:flex items-center gap-2 text-sm"):
            ui.link("Home", "/").style("color: var(--ta-muted); text-decoration:none")
            ui.icon("chevron_right").classes("text-base").style("color: var(--ta-muted-2)")
            ui.label(title).style("color: var(--ta-text)")


# ------------------------------------------------------------------ hosting footer
def hosting_footer() -> None:
    state = {"resources": initial_resources(), "loading": False,
             "updated": "Not yet measured", "error": ""}

    with ui.element("div").classes("w-full mt-6").style(
        "background:#fff; border:1px solid var(--ta-border); border-radius:1rem"
    ) as card:
        with ui.expansion("Hosting resources", icon="dns").classes("w-full").props(
            "group=hosting"
        ) as expansion:
            rows_container = ui.column().classes("w-full gap-2")

            def render_rows():
                rows_container.clear()
                with rows_container:
                    for r in state["resources"]:
                        with ui.row().classes(
                            "items-center justify-between w-full no-wrap py-3"
                        ).style("border-bottom:1px solid var(--ta-border)"):
                            with ui.row().classes("items-center gap-2"):
                                ui.icon(r["icon"]).classes("text-base").style(
                                    "color: var(--ta-muted)"
                                )
                                ui.label(r["label"]).classes(
                                    "text-sm font-medium"
                                ).style("color: var(--ta-text)")
                            with ui.row().classes("items-center gap-3"):
                                color_cls = {
                                    "green": "green", "orange": "amber",
                                    "red": "red", "gray": "gray",
                                }.get(r["color"], "gray")
                                with ui.element("span").classes(f"ta-badge {color_cls}"):
                                    ui.label(r["badge"])
                                ui.label(r["quota"]).classes(
                                    "text-sm font-medium"
                                ).style("color: var(--ta-text)")
                            ui.label(r["note"]).classes("text-xs").style(
                                "color: var(--ta-muted)"
                            )

            async def refresh():
                if state["loading"]:
                    return
                state["loading"] = True
                refresh_btn.props("disable")
                try:
                    state["resources"] = await collect_metrics()
                    from datetime import datetime, timezone

                    now = datetime.now(timezone.utc)
                    state["updated"] = now.strftime("%Y-%m-%d %H:%M:%S UTC")
                    state["error"] = ""
                except Exception:
                    state["error"] = "Refresh failed."
                finally:
                    state["loading"] = False
                    refresh_btn.props(remove="disable")
                    render_rows()
                    updated_label.text = f"Last updated: {state['updated']}"

            render_rows()
            ui.label("Runtime container usage; disk is mounted filesystem capacity, not account plan quota.").classes(
                "mt-3 text-xs"
            ).style("color: var(--ta-muted)")
            with ui.row().classes("items-center justify-between w-full mt-4 pt-3").style(
                "border-top:1px solid var(--ta-border)"
            ):
                updated_label = ui.label(f"Last updated: {state['updated']}").classes(
                    "text-xs"
                ).style("color: var(--ta-muted)")
                refresh_btn = ui.button("Refresh", icon="refresh", on_click=refresh).props(
                    "flat dense"
                ).style("color: var(--ta-primary)")


def footer_links() -> None:
    state = {"links": [], "loading": False, "error": ""}

    container = ui.element("footer").classes(
        "w-full mt-4 pt-4 flex flex-wrap items-center justify-center"
    ).style("gap: .5rem 1.25rem")

    async def load():
        if state["loading"]:
            return
        state["loading"] = True
        try:
            import asyncio

            from .footer_service import fetch_links

            links = await asyncio.to_thread(fetch_links)
            state["links"] = links
        except Exception:
            state["error"] = "Unable to refresh footer links."
        finally:
            state["loading"] = False
            render()

    def render():
        container.clear()
        with container:
            for item in state["links"]:
                ui.link(item["label"], item["url"], new_tab=True).classes(
                    "text-xs font-medium"
                ).style("color: var(--ta-primary); text-decoration:none")

    render()
    ui.timer(0.1, load, once=True)


# ------------------------------------------------------------------ page shell
def shell(active: str, content_builder) -> None:
    drawer = _sidebar(active)
    _header(drawer)
    with ui.column().classes("w-full p-4 lg:p-7 gap-0").style("background: var(--ta-bg)"):
        content_builder()
        hosting_footer()
        footer_links()