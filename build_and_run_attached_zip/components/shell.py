import reflex as rx
from build_and_run_attached_zip.states.shell_state import ShellState
from build_and_run_attached_zip.states.local_auth_state import LocalAuthState
from build_and_run_attached_zip.components.hosting_footer import hosting_footer
from build_and_run_attached_zip.components.footer_links import footer_links


def nav_link(label: str, icon: str, href: str, active: bool) -> rx.Component:
    return rx.el.a(
        rx.icon(icon, class_name="h-5 w-5 shrink-0"),
        rx.el.span(label),
        href=href,
        on_click=ShellState.close_mobile,
        aria_current=rx.cond(active, "page", "false"),
        class_name=rx.cond(
            active,
            "flex items-center gap-3 rounded-lg bg-[#465FFF]/10 px-3 py-3 text-sm font-medium text-[#465FFF] focus-visible:ring-2 focus-visible:ring-[#465FFF]",
            "flex items-center gap-3 rounded-lg px-3 py-3 text-sm font-medium text-gray-600 hover:bg-gray-100 focus-visible:ring-2 focus-visible:ring-[#465FFF]",
        ),
    )


def sidebar(active: str) -> rx.Component:
    return rx.el.aside(
        rx.el.a(
            rx.el.div(
                rx.icon(
                    "chart-no-axes-column-increasing",
                    class_name="h-6 w-6 text-white",
                ),
                class_name="flex h-10 w-10 items-center justify-center rounded-xl bg-[#465FFF]",
            ),
            rx.el.span(
                "TailAdmin",
                class_name="text-2xl font-bold tracking-tight text-[#1D2939]",
            ),
            href="/",
            on_click=ShellState.close_mobile,
            class_name="flex h-20 shrink-0 items-center gap-3 px-6 focus-visible:ring-2 focus-visible:ring-[#465FFF]",
        ),
        rx.el.nav(
            rx.el.p(
                "MENU",
                class_name="mb-4 px-3 text-xs font-medium tracking-wider text-gray-500",
            ),
            rx.el.button(
                rx.el.span(
                    rx.icon("layout-grid", class_name="h-5 w-5"),
                    "Dashboard",
                    class_name="flex items-center gap-3",
                ),
                rx.icon(
                    "chevron-down",
                    class_name=rx.cond(
                        ShellState.dashboard_open,
                        "h-4 w-4 rotate-180 transition-transform",
                        "h-4 w-4 transition-transform",
                    ),
                ),
                on_click=ShellState.toggle_dashboard,
                aria_expanded=ShellState.dashboard_open,
                class_name=rx.cond(
                    active == "Ecommerce",
                    "flex w-full items-center justify-between rounded-lg bg-[#465FFF]/10 px-3 py-3 text-sm font-medium text-[#465FFF] focus-visible:ring-2 focus-visible:ring-[#465FFF]",
                    "flex w-full items-center justify-between rounded-lg px-3 py-3 text-sm font-medium text-gray-600 hover:bg-gray-100 focus-visible:ring-2 focus-visible:ring-[#465FFF]",
                ),
            ),
            rx.cond(
                ShellState.dashboard_open,
                rx.el.a(
                    "Ecommerce",
                    href="/",
                    on_click=ShellState.close_mobile,
                    class_name=rx.cond(
                        active == "Ecommerce",
                        "my-2 ml-9 block rounded-lg bg-[#465FFF]/10 px-3 py-2.5 text-sm font-medium text-[#465FFF] focus-visible:ring-2 focus-visible:ring-[#465FFF]",
                        "my-2 ml-9 block rounded-lg px-3 py-2.5 text-sm text-gray-600 hover:bg-gray-100 focus-visible:ring-2 focus-visible:ring-[#465FFF]",
                    ),
                ),
            ),
            nav_link("Menu", "list-tree", "/menu", active == "Menu"),
            nav_link("Files", "folder", "/files", active == "Files"),
            nav_link("GitHub Sync", "code", "/github", active == "GitHub Sync"),
            rx.el.p(
                "OTHERS",
                class_name="mb-3 mt-8 px-3 text-xs font-medium tracking-wider text-gray-500",
            ),
            nav_link(
                "Authentication",
                "lock-keyhole",
                "/auth",
                active == "Authentication",
            ),
            aria_label="Main navigation",
            class_name="min-h-0 flex-1 overflow-y-auto px-4 py-7",
        ),
        rx.el.div(
            rx.icon("info", class_name="mt-0.5 h-4 w-4 shrink-0 text-gray-500"),
            rx.el.p(
                "Sample dashboard · Session-only menu",
                class_name="text-xs leading-5 text-gray-500",
            ),
            class_name="mx-5 mb-6 flex shrink-0 gap-2 border-t border-gray-200 pt-5",
        ),
        class_name=rx.cond(
            ShellState.mobile_open,
            "fixed inset-y-0 left-0 z-40 flex w-64 shrink-0 flex-col border-r border-gray-200 bg-[#F9FAFB] lg:static lg:h-full",
            "hidden h-full w-64 shrink-0 flex-col border-r border-gray-200 bg-[#F9FAFB] lg:flex",
        ),
    )


def header() -> rx.Component:
    return rx.el.header(
        rx.el.button(
            rx.icon("menu", class_name="h-5 w-5"),
            aria_label="Toggle mobile navigation",
            aria_expanded=ShellState.mobile_open,
            on_click=ShellState.toggle_mobile,
            class_name="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg border border-gray-200 bg-white text-gray-600 focus-visible:ring-2 focus-visible:ring-[#465FFF] lg:hidden",
        ),
        rx.el.div(
            rx.el.form(
                rx.el.label(
                    "Search pages",
                    html_for="header-search",
                    class_name="sr-only",
                ),
                rx.icon(
                    "search",
                    class_name="pointer-events-none absolute left-3 top-3 h-4 w-4 text-gray-500",
                ),
                rx.el.input(
                    id="header-search",
                    name="search",
                    placeholder="Search or type command...",
                    class_name="h-10 w-full rounded-lg border border-gray-200 bg-[#F9FAFB] pl-10 pr-10 text-sm text-gray-700 placeholder:text-gray-400 focus:border-[#465FFF] focus:outline-hidden focus:ring-2 focus:ring-[#465FFF]/20",
                ),
                rx.el.button(
                    rx.icon("arrow-right", class_name="h-4 w-4"),
                    type="submit",
                    aria_label="Search and navigate to page",
                    class_name="absolute right-2 top-2 rounded-md p-1 text-gray-500 hover:text-[#465FFF] focus-visible:ring-2 focus-visible:ring-[#465FFF]",
                ),
                on_submit=ShellState.search_submit,
                class_name="relative w-full",
            ),
            class_name="w-full max-w-[420px]",
        ),
        rx.el.div(
            rx.el.a(
                rx.icon("lock-keyhole", class_name="h-4 w-4"),
                rx.el.span(
                    rx.cond(
                        LocalAuthState.is_authenticated, "My account", "Sign in"
                    ),
                    class_name="hidden sm:inline",
                ),
                href=rx.cond(
                    LocalAuthState.is_authenticated, "/account", "/auth"
                ),
                class_name="flex h-10 items-center gap-2 rounded-full border border-gray-200 px-4 text-sm font-medium text-gray-600 hover:bg-gray-50 focus-visible:ring-2 focus-visible:ring-[#465FFF]",
                aria_label=rx.cond(
                    LocalAuthState.is_authenticated,
                    "View your account",
                    "Sign in or create account",
                ),
            ),
            class_name="ml-auto flex shrink-0 items-center gap-3",
        ),
        class_name="flex h-20 shrink-0 items-center gap-4 border-b border-gray-200 bg-white px-4 lg:px-7",
    )


def page_title(title: str, description: str) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.el.h1(
                title,
                class_name="text-2xl font-semibold tracking-tight text-[#1D2939]",
            ),
            rx.cond(
                description != "",
                rx.el.p(
                    description,
                    class_name="mt-1.5 text-sm text-gray-500",
                ),
            ),
        ),
        rx.el.div(
            rx.el.a(
                "Home",
                href="/",
                class_name="text-gray-500 hover:text-[#465FFF] focus-visible:ring-2 focus-visible:ring-[#465FFF]",
            ),
            rx.icon("chevron-right", class_name="h-4 w-4 text-gray-400"),
            rx.el.span(title, class_name="text-gray-700"),
            class_name="hidden items-center gap-2 text-sm sm:flex",
        ),
        class_name="mb-6 flex items-center justify-between gap-4",
    )


def shell(content: rx.Component, active: str) -> rx.Component:
    return rx.el.div(
        rx.cond(
            ShellState.mobile_open,
            rx.el.button(
                aria_label="Close mobile navigation",
                on_click=ShellState.close_mobile,
                class_name="fixed inset-0 z-30 bg-black/40 lg:hidden",
            ),
        ),
        sidebar(active),
        rx.el.div(
            header(),
            rx.el.main(
                content,
                hosting_footer(),
                footer_links(),
                class_name="min-h-0 w-full min-w-0 flex-1 overflow-y-auto bg-[#F9FAFB] p-4 text-[#1D2939] lg:p-7",
            ),
            class_name="flex min-h-0 min-w-0 flex-1 flex-col",
        ),
        class_name="flex h-dvh w-full overflow-hidden bg-[#F9FAFB] font-['Inter'] text-[#1D2939]",
    )
