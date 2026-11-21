import reflex as rx
from build_and_run_attached_zip.models import (
    FileItem,
)  # Register database metadata for managed migrations.
from build_and_run_attached_zip.components.account import sign_up_entry, account_profile
from build_and_run_attached_zip.components.dashboard import dashboard
from build_and_run_attached_zip.components.menu import menu_page
from build_and_run_attached_zip.components.files import files_page
from build_and_run_attached_zip.states.files_state import FilesState
from build_and_run_attached_zip.components.shell import shell
from build_and_run_attached_zip.components.unavailable import unavailable
from build_and_run_attached_zip.states.shell_state import ShellState
from build_and_run_attached_zip.states.hosting_state import HostingState
from build_and_run_attached_zip.states.local_auth_state import LocalAuthState
from build_and_run_attached_zip.states.footer_links_state import FooterLinksState


def index() -> rx.Component:
    return shell(dashboard(), "Ecommerce")


def menu() -> rx.Component:
    return shell(menu_page(), "Menu")


def files() -> rx.Component:
    return shell(files_page(), "Files")


def github() -> rx.Component:
    return shell(
        unavailable(
            "GitHub Sync",
            "github",
            "Repository management and synchronization.",
            "The original GitHub Sync feature requires Supabase authentication and storage, along with GitHub configuration. These integrations are not enabled here, so repositories cannot be connected, saved, or synchronized.",
        ),
        "GitHub Sync",
    )


def auth() -> rx.Component:
    return shell(sign_up_entry(), "Authentication")


def account() -> rx.Component:
    return shell(account_profile(), "Authentication")


app = rx.App(
    head_components=[
        rx.el.link(rel="preconnect", href="https://fonts.googleapis.com"),
        rx.el.link(
            rel="preconnect",
            href="https://fonts.gstatic.com",
            cross_origin="",
        ),
        rx.el.link(
            href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap",
            rel="stylesheet",
        ),
    ],
)
app.add_page(
    index,
    route="/",
    title="Dashboard — TailAdmin",
    on_load=[
        ShellState.close_mobile,
        HostingState.load_metrics,
        FooterLinksState.load,
    ],
)
app.add_page(
    menu,
    route="/menu",
    title="Menu — TailAdmin",
    on_load=[
        ShellState.close_mobile,
        HostingState.load_metrics,
        FooterLinksState.load,
    ],
)
app.add_page(
    github,
    route="/github",
    title="GitHub Sync — TailAdmin",
    on_load=[
        ShellState.close_mobile,
        HostingState.load_metrics,
        FooterLinksState.load,
    ],
)
app.add_page(
    auth,
    route="/auth",
    title="Authentication — TailAdmin",
    on_load=[
        ShellState.close_mobile,
        HostingState.load_metrics,
        FooterLinksState.load,
    ],
)
app.add_page(
    account,
    route="/account",
    title="Account — TailAdmin",
    on_load=[
        LocalAuthState.guard_account,
        ShellState.close_mobile,
        HostingState.load_metrics,
        FooterLinksState.load,
    ],
)
app.add_page(
    files,
    route="/files",
    title="Files — TailAdmin",
    on_load=[
        ShellState.close_mobile,
        HostingState.load_metrics,
        FilesState.load,
        FooterLinksState.load,
    ],
)
