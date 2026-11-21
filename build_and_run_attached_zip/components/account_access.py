import reflex as rx
from build_and_run_attached_zip.components.hosting_footer import MantineProvider
from build_and_run_attached_zip.states.local_auth_state import LocalAuthState


class MantineModal(rx.Component):
    library = "@mantine/core@7.17.8"
    lib_dependencies = ["@mantine/hooks@7.17.8"]
    tag = "Modal"
    opened: rx.Var[bool]
    on_close: rx.EventHandler[lambda: []]
    title: rx.Var[str]
    centered: rx.Var[bool]
    close_on_escape: rx.Var[bool]
    close_on_click_outside: rx.Var[bool]
    with_close_button: rx.Var[bool]
    trap_focus: rx.Var[bool]
    return_focus: rx.Var[bool]
    lock_scroll: rx.Var[bool]
    class_names: rx.Var[dict[str, str]]
    close_button_props: rx.Var[dict[str, str]]


def auth_field(
    label: str, name: str, kind: str, autocomplete: str, minimum: int = 1
) -> rx.Component:
    return rx.el.div(
        rx.el.label(
            label,
            html_for=name,
            class_name="mb-2 block text-sm font-medium text-[#1D2939]",
        ),
        rx.el.input(
            id=name,
            name=name,
            type=kind,
            auto_complete=autocomplete,
            required=True,
            min_length=minimum,
            max_length=1024,
            disabled=LocalAuthState.submitting,
            class_name="w-full rounded-lg border border-gray-200 bg-white px-3 py-3 text-sm text-[#1D2939] focus:border-[#465FFF] focus:outline-hidden focus:ring-2 focus:ring-[#465FFF]/20 disabled:opacity-50",
        ),
    )


def auth_feedback() -> rx.Component:
    return rx.cond(
        LocalAuthState.error != "",
        rx.el.p(
            LocalAuthState.error,
            role="alert",
            class_name="rounded-lg bg-red-50 p-3 text-sm text-red-700",
        ),
        rx.el.div(),
    )


def submit_button(label: str) -> rx.Component:
    return rx.el.button(
        rx.cond(
            LocalAuthState.submitting,
            rx.icon("loader-circle", class_name="h-4 w-4 animate-spin"),
            rx.icon("arrow-right", class_name="h-4 w-4"),
        ),
        rx.cond(LocalAuthState.submitting, "Please wait…", label),
        type="submit",
        disabled=LocalAuthState.submitting,
        class_name="flex w-full items-center justify-center gap-2 rounded-lg bg-[#465FFF] px-4 py-3 text-sm font-semibold text-white hover:bg-[#3641D9] focus-visible:ring-2 focus-visible:ring-[#465FFF] focus-visible:ring-offset-2 disabled:cursor-wait disabled:opacity-50",
    )


def sign_in_content() -> rx.Component:
    return rx.el.div(
        rx.el.p(
            "Sign in with the email and password you created in this app.",
            class_name="text-sm leading-6 text-gray-600",
        ),
        rx.el.form(
            auth_field("Email address", "email", "email", "email"),
            auth_field("Password", "password", "password", "current-password"),
            auth_feedback(),
            submit_button("Sign in"),
            on_submit=LocalAuthState.sign_in,
            reset_on_submit=True,
            class_name="flex flex-col gap-4",
        ),
        rx.el.p(
            "New to TailAdmin? ",
            rx.el.button(
                "Sign up",
                type="button",
                on_click=LocalAuthState.open_sign_up,
                class_name="rounded-sm bg-transparent font-semibold text-[#465FFF] hover:underline focus-visible:ring-2 focus-visible:ring-[#465FFF]",
            ),
            class_name="text-center text-sm text-gray-600",
        ),
        class_name="flex flex-col gap-5",
    )


def sign_up_content() -> rx.Component:
    return rx.el.div(
        rx.el.p(
            "Create your app account immediately. Use a unique password with at least 12 characters; no email verification is required.",
            class_name="text-sm leading-6 text-gray-600",
        ),
        rx.el.form(
            auth_field("Email address", "email", "email", "email"),
            auth_field("Password", "password", "password", "new-password", 12),
            auth_field(
                "Confirm password",
                "confirm_password",
                "password",
                "new-password",
                12,
            ),
            auth_feedback(),
            submit_button("Create account"),
            on_submit=LocalAuthState.register,
            reset_on_submit=True,
            class_name="flex flex-col gap-4",
        ),
        rx.el.p(
            "Already have an account? ",
            rx.el.button(
                "Sign in",
                type="button",
                on_click=LocalAuthState.open_sign_in,
                class_name="rounded-sm bg-transparent font-semibold text-[#465FFF] hover:underline focus-visible:ring-2 focus-visible:ring-[#465FFF]",
            ),
            class_name="text-center text-sm text-gray-600",
        ),
        class_name="flex flex-col gap-5",
    )


def account_access_strip() -> rx.Component:
    return rx.el.section(
        rx.el.div(
            rx.el.div(
                rx.icon("user-round", class_name="h-5 w-5 text-[#465FFF]"),
                class_name="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-[#465FFF]/10",
            ),
            rx.el.div(
                rx.el.h2(
                    rx.cond(
                        LocalAuthState.is_authenticated,
                        LocalAuthState.display_name,
                        "Your TailAdmin account",
                    ),
                    class_name="text-sm font-semibold text-[#1D2939]",
                ),
                rx.el.p(
                    rx.cond(
                        LocalAuthState.is_authenticated,
                        LocalAuthState.email,
                        "Sign in or create an account in this app.",
                    ),
                    class_name="mt-1 text-sm text-gray-600",
                ),
            ),
            class_name="flex min-w-0 items-center gap-3",
        ),
        rx.cond(
            LocalAuthState.is_authenticated,
            rx.el.a(
                "View account",
                rx.icon("arrow-right", class_name="h-4 w-4"),
                href="/account",
                class_name="flex items-center gap-2 rounded-lg bg-[#465FFF] px-4 py-2.5 text-sm font-semibold text-white focus-visible:ring-2 focus-visible:ring-[#465FFF]",
            ),
            rx.el.div(
                rx.el.button(
                    rx.icon("log-in", class_name="h-4 w-4"),
                    "Sign in",
                    type="button",
                    on_click=LocalAuthState.open_sign_in,
                    aria_haspopup="dialog",
                    class_name="inline-flex items-center justify-center gap-2 rounded-lg border border-gray-200 bg-white px-4 py-2.5 text-sm font-semibold text-[#1D2939] hover:bg-gray-50 focus-visible:ring-2 focus-visible:ring-[#465FFF] focus-visible:ring-offset-2",
                ),
                rx.el.button(
                    rx.icon("user-plus", class_name="h-4 w-4"),
                    "Sign up",
                    type="button",
                    on_click=LocalAuthState.open_sign_up,
                    aria_haspopup="dialog",
                    class_name="inline-flex items-center justify-center gap-2 rounded-lg bg-[#465FFF] px-4 py-2.5 text-sm font-semibold text-white hover:bg-[#3641D9] focus-visible:ring-2 focus-visible:ring-[#465FFF] focus-visible:ring-offset-2",
                ),
                class_name="flex shrink-0 items-center gap-3",
            ),
        ),
        account_access_modal(),
        aria_label="Account access",
        custom_attrs={"data-testid": "account-access-strip"},
        class_name="flex w-full flex-wrap items-center justify-between gap-4 rounded-2xl border border-gray-200 bg-white px-5 py-4",
    )


def account_access_modal() -> rx.Component:
    return MantineProvider.create(
        MantineModal.create(
            rx.el.div(
                rx.cond(
                    LocalAuthState.mode == "sign_up",
                    sign_up_content(),
                    sign_in_content(),
                ),
                rx.el.div(
                    rx.icon(
                        "shield-check",
                        class_name="mt-0.5 h-4 w-4 shrink-0 text-[#465FFF]",
                    ),
                    rx.el.p(
                        "Passwords are securely hashed by this app. Password recovery is not provided. Previous external accounts and their files do not transfer to a new account.",
                        class_name="text-xs leading-5 text-gray-600",
                    ),
                    class_name="mt-6 flex gap-2 border-t border-gray-200 pt-4",
                ),
                class_name="bg-white font-['Inter'] text-[#1D2939]",
            ),
            opened=LocalAuthState.opened,
            on_close=LocalAuthState.close_modal,
            title=rx.cond(
                LocalAuthState.mode == "sign_up",
                "Create an account",
                "Sign in to TailAdmin",
            ),
            centered=True,
            close_on_escape=True,
            close_on_click_outside=True,
            with_close_button=True,
            trap_focus=True,
            return_focus=True,
            lock_scroll=True,
            close_button_props={"aria-label": "Close account access"},
            class_names={
                "content": "!rounded-2xl !border !border-gray-200 !bg-white !shadow-none font-['Inter'] text-[#1D2939]",
                "header": "!bg-white !px-6 !pt-6 !pb-4",
                "title": "!text-xl !font-semibold !text-[#1D2939]",
                "body": "!px-6 !pb-6",
                "close": "!text-gray-600 hover:!bg-gray-100 focus-visible:ring-2 focus-visible:ring-[#465FFF]",
                "overlay": "!bg-black/40",
            },
        ),
        theme={"fontFamily": "Inter, sans-serif"},
        force_color_scheme="light",
    )
