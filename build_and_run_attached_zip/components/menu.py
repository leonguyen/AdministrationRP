import reflex as rx
from build_and_run_attached_zip.components.shell import page_title
from build_and_run_attached_zip.states.menu_state import MenuState
from build_and_run_attached_zip.components.svar_grid import menu_grid, menu_toolbar


PRIMARY_BUTTON = "inline-flex items-center justify-center gap-2 rounded-lg bg-[#465FFF] px-4 py-2.5 text-sm font-medium text-white transition hover:bg-[#3641D9] focus-visible:ring-2 focus-visible:ring-[#465FFF] focus-visible:ring-offset-2"


def field(
    label: str, name: str, value: str, placeholder: str, required: bool
) -> rx.Component:
    return rx.el.div(
        rx.el.label(
            label,
            rx.cond(required, rx.el.span(" *", class_name="text-red-600")),
            html_for=name,
            class_name="mb-2 block text-sm font-medium text-gray-700",
        ),
        rx.el.input(
            id=name,
            name=name,
            default_value=value,
            key=value,
            required=required,
            placeholder=placeholder,
            auto_focus=required,
            class_name="h-11 w-full rounded-lg border border-gray-200 bg-white px-3 text-sm text-[#1D2939] placeholder:text-gray-400 focus:border-[#465FFF] focus:outline-hidden focus:ring-2 focus:ring-[#465FFF]/20",
        ),
    )


def menu_modal() -> rx.Component:
    return rx.radix.primitives.dialog.root(
        rx.radix.primitives.dialog.portal(
            rx.radix.primitives.dialog.overlay(
                class_name="fixed inset-0 z-50 bg-black/40 backdrop-blur-xs"
            ),
            rx.radix.primitives.dialog.content(
                rx.el.div(
                    rx.radix.primitives.dialog.title(
                        rx.cond(
                            MenuState.editing_id != "", "Edit Menu", "Add Menu"
                        ),
                        class_name="text-xl font-semibold text-[#1D2939]",
                    ),
                    rx.el.button(
                        rx.icon("x", class_name="h-5 w-5"),
                        on_click=MenuState.close_modal,
                        aria_label="Close menu form",
                        class_name="rounded-lg p-2 text-gray-500 hover:bg-gray-100 focus-visible:ring-2 focus-visible:ring-[#465FFF]",
                    ),
                    class_name="flex items-center justify-between gap-3",
                ),
                rx.radix.primitives.dialog.description(
                    "Define a hierarchy and its route mapping. Use / to separate levels.",
                    class_name="mt-2 text-sm leading-6 text-gray-500",
                ),
                rx.el.form(
                    field(
                        "Hierarchy Name",
                        "hierarchy_name",
                        MenuState.hierarchy_name,
                        "e.g. Users / Profile",
                        True,
                    ),
                    field(
                        "Sign in Url",
                        "sign_in_url",
                        MenuState.sign_in_url,
                        "/signin",
                        False,
                    ),
                    field(
                        "Management Url",
                        "management_url",
                        MenuState.management_url,
                        "/admin/...",
                        False,
                    ),
                    rx.cond(
                        MenuState.error != "",
                        rx.el.p(
                            MenuState.error,
                            role="alert",
                            class_name="rounded-lg bg-red-100 px-3 py-2 text-sm text-red-700",
                        ),
                    ),
                    rx.el.div(
                        rx.el.button(
                            "Cancel",
                            type="button",
                            on_click=MenuState.close_modal,
                            class_name="rounded-lg border border-gray-200 px-4 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50 focus-visible:ring-2 focus-visible:ring-[#465FFF]",
                        ),
                        rx.el.button(
                            rx.icon("check", class_name="h-4 w-4"),
                            "Save",
                            type="submit",
                            class_name=PRIMARY_BUTTON,
                        ),
                        class_name="flex justify-end gap-3 border-t border-gray-200 pt-5",
                    ),
                    on_submit=MenuState.save_menu,
                    class_name="mt-6 space-y-5",
                ),
                class_name="fixed left-1/2 top-1/2 z-50 max-h-[90dvh] w-[calc(100%-2rem)] max-w-lg -translate-x-1/2 -translate-y-1/2 overflow-y-auto rounded-2xl border border-gray-200 bg-white p-6 font-['Inter'] text-[#1D2939] focus:outline-hidden",
            ),
        ),
        open=MenuState.modal_open,
        on_open_change=MenuState.change_modal,
    )


def menu_page() -> rx.Component:
    return rx.el.div(
        page_title("Menu", "Manage menu hierarchy and route mapping."),
        rx.el.div(
            rx.el.p(
                "Menu hierarchy",
                class_name="text-lg font-semibold text-[#1D2939]",
            ),
            menu_toolbar(MenuState.toolbar_items, MenuState.toolbar_action),
            class_name="mb-5 flex flex-wrap items-center justify-between gap-4",
        ),
        rx.el.section(
            rx.el.div(
                rx.el.div(
                    rx.el.label(
                        "Search menu",
                        html_for="menu-search",
                        class_name="sr-only",
                    ),
                    rx.icon(
                        "search",
                        class_name="pointer-events-none absolute left-3 top-3 h-4 w-4 text-gray-400",
                    ),
                    rx.el.input(
                        id="menu-search",
                        placeholder="Search menu...",
                        default_value=MenuState.query,
                        on_change=MenuState.set_query.debounce(300),
                        class_name="h-10 w-full rounded-lg border border-gray-200 bg-[#F9FAFB] pl-10 pr-10 text-sm text-[#1D2939] focus:border-[#465FFF] focus:outline-hidden focus:ring-2 focus:ring-[#465FFF]/20",
                    ),
                    rx.cond(
                        MenuState.query != "",
                        rx.el.button(
                            rx.icon("x", class_name="h-4 w-4"),
                            on_click=MenuState.clear_search,
                            aria_label="Clear menu search",
                            class_name="absolute right-2 top-2 rounded-md p-1 text-gray-500 hover:text-[#465FFF] focus-visible:ring-2 focus-visible:ring-[#465FFF]",
                        ),
                    ),
                    class_name="relative w-full max-w-sm",
                ),
                rx.el.span(
                    f"{MenuState.filtered_rows.length()} items",
                    aria_live="polite",
                    class_name="shrink-0 text-sm text-gray-500",
                ),
                class_name="flex items-center justify-between gap-4 border-b border-gray-200 p-5",
            ),
            rx.el.div(
                menu_grid(
                    MenuState.filtered_rows,
                    MenuState.selected_rows,
                    MenuState.select_row,
                ),
                class_name="w-full overflow-x-auto",
            ),
            rx.cond(
                MenuState.filtered_rows.length() == 0,
                rx.el.div(
                    rx.el.div(
                        rx.icon(
                            "list-tree", class_name="h-7 w-7 text-gray-400"
                        ),
                        class_name="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-gray-100",
                    ),
                    rx.el.h2(
                        "No menus found",
                        class_name="text-base font-semibold text-[#1D2939]",
                    ),
                    rx.el.p(
                        rx.cond(
                            MenuState.query != "",
                            "Try a different name or URL, or clear your search.",
                            "Add your first menu to create a hierarchy and route mapping.",
                        ),
                        class_name="mt-2 text-sm text-gray-500",
                    ),
                    rx.el.button(
                        "Add Menu",
                        on_click=MenuState.start_create,
                        class_name="mt-5 rounded-lg px-4 py-2 text-sm font-medium text-[#465FFF] hover:bg-indigo-50 focus-visible:ring-2 focus-visible:ring-[#465FFF]",
                    ),
                    class_name="px-6 py-16 text-center",
                ),
            ),
            class_name="overflow-hidden rounded-2xl border border-gray-200 bg-white",
        ),
        rx.el.p(
            rx.icon("info", class_name="h-4 w-4 shrink-0"),
            "Changes are kept in this session only and reset on reload. URLs are route mappings, not active navigation links.",
            class_name="mt-5 flex items-start gap-2 text-xs leading-5 text-gray-500",
        ),
        menu_modal(),
        class_name="w-full min-w-0",
    )
