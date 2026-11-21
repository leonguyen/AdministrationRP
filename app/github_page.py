"""GitHub Sync placeholder page (feature unavailable).

Ported from the Reflex app's unavailable.py / github route.
"""
from nicegui import ui

from .layout import page_title


def github_content():
    with ui.column().classes("w-full"):
        page_title(
            "GitHub Sync",
            "Repository management and synchronization.",
        )
        with ui.element("section").classes("w-full").style(
            "display:flex; align-items:center; min-height:480px; background:#fff; "
            "border:1px solid var(--ta-border); border-radius:1rem; padding:1.5rem 2.5rem"
        ):
            with ui.column().classes("w-full max-w-3xl"):
                with ui.element("div").classes(
                    "mb-6 flex items-center justify-center rounded-2xl"
                ).style("width:4rem;height:4rem;background:#EEF2FF"):
                    ui.icon("code").classes("text-3xl").style("color: var(--ta-primary)")
                with ui.element("span").classes(
                    "mb-4 inline-flex w-fit items-center gap-2 rounded-full px-3 py-1.5 text-xs font-medium"
                ).style("background:#FEF3C7; color:#92400E"):
                    ui.icon("error").classes("text-sm")
                    ui.label("Feature unavailable")
                ui.label("GitHub Sync is not enabled").classes(
                    "text-2xl font-semibold tracking-tight"
                ).style("color: var(--ta-text)")
                ui.label(
                    "The original GitHub Sync feature requires Supabase authentication "
                    "and storage, along with GitHub configuration. These integrations "
                    "are not enabled here, so repositories cannot be connected, saved, "
                    "or synchronized."
                ).classes("mt-4 max-w-2xl text-base leading-7").style("color: var(--ta-muted)")

                with ui.row().classes(
                    "mt-7 gap-3 rounded-xl p-5"
                ).style("border:1px solid var(--ta-border); background: var(--ta-bg)"):
                    ui.icon("verified_user").classes("mt-0.5 text-xl shrink-0").style(
                        "color: var(--ta-primary)"
                    )
                    with ui.column().classes("gap-1"):
                        ui.label("No GitHub repository activity is performed").classes(
                            "text-sm font-semibold"
                        ).style("color: var(--ta-text)")
                        ui.label(
                            "GitHub connections, repository saving, commits, merges, and "
                            "GitHub requests are not simulated or executed."
                        ).classes("text-sm leading-6").style("color: var(--ta-muted)")

                with ui.row().classes("mt-8 flex-wrap gap-3"):
                    ui.link("Back to dashboard", "/").classes(
                        "ta-btn-primary"
                    ).style("text-decoration:none")
                    ui.link("Manage menu", "/menu").classes(
                        "ta-btn"
                    ).style("text-decoration:none")


def build():
    from .layout import shell

    shell("GitHub Sync", github_content)