import reflex as rx
from build_and_run_attached_zip.components.shell import page_title
from build_and_run_attached_zip.components.account_access import account_access_modal
from build_and_run_attached_zip.states.local_auth_state import LocalAuthState


def sign_up_entry() -> rx.Component:
    return rx.el.div(
        page_title(
            "Authentication", "Email and password accounts for this app."
        ),
        account_access_modal(),
        rx.el.section(
            rx.el.div(
                rx.el.div(
                    rx.icon("user-plus", class_name="h-8 w-8 text-[#465FFF]"),
                    class_name="mb-6 flex h-16 w-16 items-center justify-center rounded-2xl bg-indigo-50",
                ),
                rx.el.h2(
                    "Create your account",
                    class_name="text-3xl font-semibold tracking-tight text-[#1D2939]",
                ),
                rx.el.p(
                    "Create an account with your email and a unique password of at least 12 characters. Sign-up creates your account immediately; no verification email is sent.",
                    class_name="mt-4 text-base leading-7 text-gray-600",
                ),
                rx.el.div(
                    rx.icon(
                        "shield-check",
                        class_name="mt-0.5 h-5 w-5 shrink-0 text-[#465FFF]",
                    ),
                    rx.el.p(
                        "Credentials belong to this app. Passwords are securely hashed. Password recovery is not provided, so keep your password safe.",
                        class_name="text-sm leading-6 text-gray-600",
                    ),
                    class_name="mt-6 flex gap-3 rounded-xl border border-gray-200 bg-[#F9FAFB] p-5",
                ),
                rx.el.p(
                    "Your account, one secure next step.",
                    class_name="mt-7 text-sm font-medium text-[#1D2939]",
                ),
                rx.el.p(
                    "Previous external identities are revoked. Matching an old email does not transfer an account or grant access to its files.",
                    class_name="mt-2 text-sm leading-6 text-gray-600",
                ),
                class_name="w-full min-w-0 lg:py-8",
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.span(
                        rx.icon("shield-check", class_name="h-4 w-4"),
                        "SECURE SIGN UP",
                        class_name="inline-flex w-fit items-center gap-2 rounded-full bg-indigo-50 px-3 py-1.5 text-xs font-semibold tracking-wide text-[#465FFF]",
                    ),
                    rx.el.h3(
                        "Ready to get started?",
                        id="secure-signup-title",
                        class_name="mt-5 text-xl font-semibold leading-8 tracking-tight text-[#1D2939]",
                    ),
                    rx.el.p(
                        "Open the form to enter your credentials in this app.",
                        id="signup-preview-description",
                        class_name="mt-2 text-sm font-medium leading-6 text-gray-600",
                    ),
                    class_name="mb-7",
                ),
                rx.el.p(
                    "Your new account has its own private file workspace. Old file ownership remains unchanged.",
                    class_name="text-sm leading-6 text-gray-600",
                ),
                rx.el.button(
                    "Create account",
                    rx.icon("arrow-right", class_name="h-4 w-4"),
                    type="button",
                    on_click=LocalAuthState.open_sign_up,
                    class_name="mt-7 flex w-full items-center justify-center gap-2 rounded-lg bg-[#465FFF] px-4 py-3.5 text-sm font-semibold text-white transition-colors hover:bg-[#3641D9] focus-visible:ring-2 focus-visible:ring-[#465FFF] focus-visible:ring-offset-2",
                ),
                rx.el.p(
                    "Already have an account? ",
                    rx.el.button(
                        "Sign in",
                        type="button",
                        on_click=LocalAuthState.open_sign_in,
                        class_name="font-medium text-[#465FFF] hover:underline focus-visible:ring-2 focus-visible:ring-[#465FFF]",
                    ),
                    class_name="mt-5 text-center text-sm leading-6 text-gray-600",
                ),
                rx.el.div(
                    rx.icon(
                        "lock-keyhole",
                        class_name="mt-0.5 h-4 w-4 shrink-0 text-[#465FFF]",
                    ),
                    rx.el.p(
                        "Use the sign-up or sign-in modal. Your password is never saved in browser storage or app state.",
                        class_name="text-xs leading-5 text-gray-600",
                    ),
                    class_name="mt-6 flex gap-2 border-t border-gray-200 pt-5",
                ),
                aria_labelledby="secure-signup-title",
                class_name="w-full min-w-0 rounded-2xl border border-gray-200 bg-white p-5 sm:p-8",
            ),
            class_name="grid w-full grid-cols-1 items-center gap-8 rounded-2xl border border-gray-200 bg-white p-6 sm:p-10 xl:grid-cols-2 xl:gap-12 xl:p-12",
        ),
        class_name="w-full",
    )


def login_required() -> rx.Component:
    return rx.el.section(
        rx.icon("lock-keyhole", class_name="mb-4 h-7 w-7 text-[#465FFF]"),
        rx.el.h1(
            "Sign in required",
            class_name="text-2xl font-semibold text-[#1D2939]",
        ),
        rx.el.p(
            "Sign in to access your account and private files.",
            class_name="mt-3 text-sm text-gray-600",
        ),
        rx.el.a(
            "Sign in or create account",
            href="/auth",
            class_name="mt-5 inline-flex rounded-lg bg-[#465FFF] px-4 py-3 text-sm font-semibold text-white focus-visible:ring-2 focus-visible:ring-[#465FFF]",
        ),
        class_name="rounded-2xl border border-gray-200 bg-white p-6",
    )


def account_profile() -> rx.Component:
    return rx.cond(
        LocalAuthState.is_authenticated, profile_details(), login_required()
    )


def profile_details() -> rx.Component:
    return rx.el.div(
        page_title("Account", "Account information and access."),
        rx.el.section(
            rx.el.div(
                rx.icon("user-round", class_name="h-7 w-7 text-[#465FFF]"),
                class_name="mb-5 flex h-14 w-14 items-center justify-center rounded-2xl bg-indigo-50",
            ),
            rx.el.span(
                "Signed in",
                class_name="mb-4 inline-flex w-fit items-center gap-2 rounded-full bg-green-100 px-3 py-1.5 text-xs font-medium text-green-800",
            ),
            rx.el.h2(
                "Welcome to your account",
                class_name="text-2xl font-semibold text-[#1D2939]",
            ),
            rx.el.dl(
                rx.el.div(
                    rx.el.dt(
                        "Name", class_name="text-sm font-medium text-gray-600"
                    ),
                    rx.el.dd(
                        LocalAuthState.display_name,
                        class_name="mt-1 break-words text-base font-medium text-[#1D2939]",
                    ),
                    class_name="border-b border-gray-200 py-4",
                ),
                rx.el.div(
                    rx.el.dt(
                        "Email", class_name="text-sm font-medium text-gray-600"
                    ),
                    rx.el.dd(
                        LocalAuthState.email,
                        class_name="mt-1 break-words text-base font-medium text-[#1D2939]",
                    ),
                    class_name="py-4",
                ),
                class_name="mt-5 w-full",
            ),
            rx.el.p(
                "This is your local app account. Files are private to this account. Password recovery is not available.",
                class_name="mt-4 text-sm leading-6 text-gray-600",
            ),
            rx.el.button(
                rx.icon("log-out", class_name="h-4 w-4"),
                "Log out",
                on_click=LocalAuthState.logout,
                type="button",
                class_name="mt-7 inline-flex items-center gap-2 rounded-lg border border-gray-200 bg-white px-5 py-3 text-sm font-medium text-gray-700 hover:bg-gray-50 focus-visible:ring-2 focus-visible:ring-[#465FFF]",
            ),
            class_name="w-full rounded-2xl border border-gray-200 bg-white p-6 sm:p-10",
        ),
        class_name="w-full",
    )
