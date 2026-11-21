"""Authentication + account pages.

Ported from the Reflex app's account.py, account_access.py, and LocalAuthState.
Sign-in/sign-up use a modal; on success the account id is stored in the browser
session and the user is redirected to /account.
"""
from nicegui import ui

from .layout import page_title
from . import session
from .auth_service import authenticate


def _auth_modal(initial_mode="sign_in"):
    state = {"mode": initial_mode}

    with ui.dialog() as dialog, ui.card().classes("w-full").style(
        "max-width:28rem; border-radius:1rem"
    ):
        title = ui.label("").classes("text-xl font-semibold").style("color: var(--ta-text)")
        error_box = ui.label("").classes("text-sm").style(
            "color:#B91C1C; background:#FEF2F2; border-radius:.5rem; padding:.5rem .75rem; display:none"
        )
        intro = ui.label("").classes("text-sm leading-6").style("color: #4B5563")

        form = ui.column().classes("w-full gap-4 mt-2")
        with form:
            email_input = ui.input("Email address").props(
                "outlined dense type=email autocomplete=email"
            ).classes("w-full")
            password_input = ui.input("Password").props(
                "outlined dense type=password autocomplete=current-password"
            ).classes("w-full")
            confirm_row = ui.column().classes("w-full")
            with confirm_row:
                confirm_input = ui.input("Confirm password").props(
                    "outlined dense type=password autocomplete=new-password"
                ).classes("w-full")

        submit_btn = ui.button("Sign in", on_click=lambda: None).classes(
            "ta-btn-primary w-full"
        )
        switch_row = ui.row().classes(
            "text-center text-sm w-full justify-center"
        )

        def render_switch():
            switch_row.clear()
            with switch_row:
                if state["mode"] == "sign_in":
                    ui.label("New to TailAdmin? ").style("color: #4B5563")
                    ui.button("Sign up", on_click=lambda: set_mode("sign_up")).props(
                        "flat dense no-caps"
                    ).style("color: var(--ta-primary); padding:0; min-width:0")
                else:
                    ui.label("Already have an account? ").style("color: #4B5563")
                    ui.button("Sign in", on_click=lambda: set_mode("sign_in")).props(
                        "flat dense no-caps"
                    ).style("color: var(--ta-primary); padding:0; min-width:0")

        def set_mode(mode):
            state["mode"] = mode
            error_box.style("display:none")
            if mode == "sign_up":
                title.text = "Create an account"
                intro.text = (
                    "Create your app account immediately. Use a unique password with at "
                    "least 12 characters; no email verification is required."
                )
                password_input.props("autocomplete=new-password")
                password_input.props(add="minlength=12")
                confirm_row.set_visibility(True)
                submit_btn.text = "Create account"
            else:
                title.text = "Sign in to TailAdmin"
                intro.text = "Sign in with the email and password you created in this app."
                password_input.props(remove="minlength=12")
                password_input.props("autocomplete=current-password")
                confirm_row.set_visibility(False)
                submit_btn.text = "Sign in"
            render_switch()

        def submit():
            signup = state["mode"] == "sign_up"
            error_box.style("display:none")
            try:
                account_id, email, name = authenticate(
                    email_input.value or "",
                    password_input.value or "",
                    confirm_input.value or "",
                    signup,
                )
                session.set_account(account_id)
                dialog.close()
                ui.navigate.to("/account")
            except ValueError as e:
                msg = str(e) if signup else (
                    str(e) if "email" in str(e).lower() else
                    "Unable to sign in. Check your credentials or try again later."
                )
                error_box.text = msg
                error_box.style("display:block")

        submit_btn.on_click(submit)
        password_input.on("keydown.enter", submit)
        email_input.on("keydown.enter", submit)
        confirm_input.on("keydown.enter", submit)

        ui.label(
            "Passwords are securely hashed by this app. Password recovery is not "
            "provided."
        ).classes("mt-6 pt-4 text-xs leading-5").style(
            "color:#4B5563; border-top:1px solid var(--ta-border)"
        )

    set_mode(initial_mode)
    return dialog


def auth_content():
    page_title("Authentication", "Email and password accounts for this app.")

    with ui.grid().classes(
        "w-full grid-cols-1 xl:grid-cols-2 gap-8 rounded-2xl p-6 sm:p-10"
    ).style("background:#fff; border:1px solid var(--ta-border)"):
        with ui.column().classes("min-w-0 lg:py-8"):
            with ui.element("div").classes(
                "mb-6 flex items-center justify-center rounded-2xl"
            ).style("width:4rem;height:4rem;background:#EEF2FF"):
                ui.icon("person_add").classes("text-3xl").style("color: var(--ta-primary)")
            ui.label("Create your account").classes(
                "text-3xl font-semibold tracking-tight"
            ).style("color: var(--ta-text)")
            ui.label(
                "Create an account with your email and a unique password of at least 12 "
                "characters. Sign-up creates your account immediately; no verification "
                "email is sent."
            ).classes("mt-4 text-base leading-7").style("color: #4B5563")
            with ui.row().classes(
                "mt-6 gap-3 rounded-xl p-5"
            ).style("border:1px solid var(--ta-border); background: var(--ta-bg)"):
                ui.icon("verified_user").classes("mt-0.5 text-xl shrink-0").style(
                    "color: var(--ta-primary)"
                )
                ui.label(
                    "Credentials belong to this app. Passwords are securely hashed. "
                    "Password recovery is not provided, so keep your password safe."
                ).classes("text-sm leading-6").style("color: #4B5563")
            ui.label("Your account, one secure next step.").classes(
                "mt-7 text-sm font-medium"
            ).style("color: var(--ta-text)")
            ui.label(
                "Previous external identities are revoked. Matching an old email does "
                "not transfer an account or grant access to its files."
            ).classes("mt-2 text-sm leading-6").style("color: #4B5563")

        with ui.card().classes("w-full min-w-0 p-5 sm:p-8").style(
            "border-radius:1rem; border:1px solid var(--ta-border); background:#fff"
        ):
            with ui.element("span").classes(
                "inline-flex w-fit items-center gap-2 rounded-full px-3 py-1.5 text-xs font-semibold tracking-wide"
            ).style("background:#EEF2FF; color: var(--ta-primary)"):
                ui.icon("verified_user").classes("text-base")
                ui.label("SECURE SIGN UP")
            ui.label("Ready to get started?").classes(
                "mt-5 text-xl font-semibold leading-8 tracking-tight"
            ).style("color: var(--ta-text)")
            ui.label(
                "Open the form to enter your credentials in this app."
            ).classes("mt-2 text-sm font-medium leading-6").style("color: #4B5563")
            ui.label(
                "Your new account has its own private file workspace."
            ).classes("text-sm leading-6").style("color: #4B5563")

            def open_modal(mode):
                d = _auth_modal(mode)
                d.open()

            ui.button("Create account", icon="arrow_forward",
                      on_click=lambda: open_modal("sign_up")).classes(
                "ta-btn-primary mt-7 w-full"
            ).style("padding:.875rem 1rem; font-weight:600")
            with ui.row().classes("mt-5 text-sm leading-6 justify-center"):
                ui.label("Already have an account? ").style("color: #4B5563")
                ui.button("Sign in", on_click=lambda: open_modal("sign_in")).props(
                    "flat dense no-caps"
                ).style("color: var(--ta-primary); font-weight:500; padding:0; min-width:0")
            with ui.row().classes(
                "mt-6 gap-2 pt-5"
            ).style("border-top:1px solid var(--ta-border)"):
                ui.icon("lock").classes("mt-0.5 text-base shrink-0").style(
                    "color: var(--ta-primary)"
                )
                ui.label(
                    "Use the sign-up or sign-in modal. Your password is never saved in "
                    "browser storage or app state."
                ).classes("text-xs leading-5").style("color:#4B5563")


def account_content():
    if not session.is_authenticated():
        _login_required()
        return
    profile = session.current_profile()
    _, email, name = profile
    display = name or email

    with ui.column().classes("w-full"):
        page_title("Account", "Account information and access.")
        with ui.card().classes("w-full p-6 sm:p-10").style(
            "border-radius:1rem; border:1px solid var(--ta-border); background:#fff"
        ):
            with ui.element("div").classes(
                "mb-5 flex items-center justify-center rounded-2xl"
            ).style("width:3.5rem;height:3.5rem;background:#EEF2FF"):
                ui.icon("person").classes("text-2xl").style("color: var(--ta-primary)")
            with ui.element("span").classes(
                "mb-4 inline-flex w-fit items-center gap-2 rounded-full px-3 py-1.5 text-xs font-medium"
            ).style("background:#DCFCE7; color:#166534"):
                ui.label("Signed in")
            ui.label("Welcome to your account").classes(
                "text-2xl font-semibold"
            ).style("color: var(--ta-text)")

            with ui.column().classes("mt-5 w-full"):
                with ui.column().classes("py-4").style("border-bottom:1px solid var(--ta-border)"):
                    ui.label("Name").classes("text-sm font-medium").style("color:#4B5563")
                    ui.label(display).classes(
                        "mt-1 text-base font-medium break-words"
                    ).style("color: var(--ta-text)")
                with ui.column().classes("py-4"):
                    ui.label("Email").classes("text-sm font-medium").style("color:#4B5563")
                    ui.label(email).classes(
                        "mt-1 text-base font-medium break-words"
                    ).style("color: var(--ta-text)")

            ui.label(
                "This is your local app account. Files are private to this account. "
                "Password recovery is not available."
            ).classes("mt-4 text-sm leading-6").style("color:#4B5563")

            def logout():
                session.clear_account()
                session.clear_files_view()
                ui.navigate.to("/")

            ui.button("Log out", icon="logout", on_click=logout).classes(
                "ta-btn mt-7"
            )


def _login_required():
    with ui.element("section").classes("w-full").style(
        "background:#fff; border:1px solid var(--ta-border); border-radius:1rem; padding:1.5rem"
    ):
        ui.icon("lock").classes("text-3xl mb-4").style("color: var(--ta-primary)")
        ui.label("Sign in required").classes("text-2xl font-semibold").style(
            "color: var(--ta-text)"
        )
        ui.label("Sign in to access your account and private files.").classes(
            "mt-3 text-sm"
        ).style("color: var(--ta-muted)")
        ui.link("Sign in or create account", "/auth").classes(
            "mt-5 inline-flex rounded-lg px-4 py-3 text-sm font-semibold text-white"
        ).style("background: var(--ta-primary); text-decoration:none")


def auth_build():
    from .layout import shell

    shell("Authentication", auth_content)


def account_build():
    from .layout import shell

    shell("Authentication", account_content)