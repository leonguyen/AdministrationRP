"""Per-user and per-tab session state for NiceGUI.

- account_id is stored in app.storage.user (browser-scoped, persists across
  reloads and is shared by tabs of the same browser) so sign-in survives reloads.
- Transient view state (current folder, selection, menu rows) lives in
  app.storage.tab (per-connection) for simplicity.
"""
from nicegui import app

from . import auth_service, files_service

ACCOUNT_KEY = "account_id"


# ---------------------------------------------------------------- account identity
def get_account_id() -> str:
    try:
        return app.storage.user.get(ACCOUNT_KEY, "") or ""
    except Exception:
        return ""


def is_authenticated() -> bool:
    return bool(get_account_id())


def set_account(account_id: str) -> None:
    app.storage.user[ACCOUNT_KEY] = account_id


def clear_account() -> None:
    app.storage.user.pop(ACCOUNT_KEY, None)


def current_profile() -> tuple[str, str, str]:
    """Return a fresh (id, email, display_name), validating against the DB."""
    account_id = get_account_id()
    profile = auth_service.get_profile(account_id)
    if not profile[0] and account_id:
        # Account disappeared (e.g. DB reset) -> clear stale identity.
        clear_account()
    return profile


def display_name() -> str:
    _, email, name = current_profile()
    return (name or email) if email else ""


# ---------------------------------------------------------------- per-tab view state
def tab_state() -> dict:
    """A per-connection dict for transient view state."""
    try:
        return app.storage.tab
    except Exception:
        return {}


def menu_rows() -> list[dict]:
    """Session-only menu rows (reset on reload), stored per tab."""
    st = tab_state()
    if "menu_rows" not in st:
        from .menu_data import initial_rows

        st["menu_rows"] = [dict(r) for r in initial_rows()]
    return st["menu_rows"]


def files_view() -> dict:
    st = tab_state()
    if "files_view" not in st:
        st["files_view"] = {
            "current_path": "/",
            "selected_path": "",
            "selected_name": "",
            "selected_is_folder": False,
            "items": [],
            "loaded": False,
            "busy": False,
            "error": "",
            "delete_confirmation": False,
            "revision": 0,
        }
    return st["files_view"]


def clear_files_view() -> None:
    st = tab_state()
    st.pop("files_view", None)


# ---------------------------------------------------------------- files helpers
def _drive(items: list[dict]) -> dict[str, int]:
    used = sum(item["size"] for item in items if item["type"] == "file")
    return {"used": used, "total": used}


def storage_label(items: list[dict]) -> str:
    used = _drive(items)["used"]
    if used >= 1024 * 1024:
        return f"{used / (1024 * 1024):.2f} MB"
    if used >= 1024:
        return f"{used / 1024:.2f} KB"
    return f"{used} B"


def folder_is_empty(items: list[dict], current_path: str) -> bool:
    return not any(
        item["id"].rsplit("/", 1)[0] == current_path.rstrip("/") for item in items
    )


def run_file_op(operation: str, name: str = "", target: str = "",
                uploads: list[tuple[str, bytes, str]] | None = None) -> tuple:
    """Run a file operation for the current account. Returns (metadata, next_path, dl_name, dl_bytes)."""
    return files_service.execute(
        get_account_id(), operation, name, target, uploads or []
    )


def mime_for(name: str) -> str:
    return files_service.mime_for(name)