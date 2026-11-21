"""Files page: DB-backed file manager (folders, upload, rename, delete, download).

Ported from the Reflex app's files.py (svar filemanager -> NiceGUI table).
Auth-guarded: signed-out users see a login-required prompt.
"""
import asyncio

from nicegui import ui

from .layout import page_title
from . import session
from .files_service import MAX_FILE_SIZE, MAX_UPLOAD_FILES

BUTTON = "ta-btn"
PRIMARY = "ta-btn-primary"


def login_required():
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


def files_content():
    if not session.is_authenticated():
        login_required()
        return
    _private_files()


def _format_size(n: int) -> str:
    if n >= 1024 * 1024:
        return f"{n / (1024 * 1024):.2f} MB"
    if n >= 1024:
        return f"{n / 1024:.2f} KB"
    return f"{n} B"


def _private_files():
    view = session.files_view()

    with ui.column().classes("w-full min-w-0 gap-0"):
        page_title("Files", "Your private workspace for files and folders.")

        # Storage header
        with ui.element("section").classes("w-full mb-6").style(
            "background:#fff; border:1px solid var(--ta-border); border-radius:1rem; padding:1.25rem"
        ):
            with ui.row().classes("items-center justify-between w-full mb-4 no-wrap"):
                with ui.row().classes("items-center gap-2"):
                    ui.icon("hard_drive").classes("text-xl").style("color: var(--ta-primary)")
                    ui.label("My files").classes("ta-section-title")
                storage_label = ui.label("").classes(
                    "w-fit rounded-full px-3 py-1 text-xs font-medium"
                ).style("background: var(--ta-soft); color: #4B5563")

            ui.label(
                "Persistent storage belongs to your signed-in account only. Files are "
                "saved across reloads. Duplicate names within a folder are not allowed."
            ).classes("mb-5 text-sm leading-6").style("color: var(--ta-muted)")

            # Upload area
            upload = ui.upload(
                on_multi_upload=lambda e: asyncio.create_task(_on_uploaded(e)),
                multiple=True,
                max_files=MAX_UPLOAD_FILES,
                max_file_size=MAX_FILE_SIZE,
                auto_upload=False,
            ).props("accept=*").classes("w-full").style(
                "border:1px dashed #D1D5DB; border-radius:.75rem; padding:1.25rem"
            )
            with upload:
                ui.icon("cloud_upload").classes("text-3xl").style("color: var(--ta-primary)")
                ui.label("Click to choose files, or drag them here").classes(
                    "text-sm font-medium"
                ).style("color: #374151")
                ui.label(
                    f"Up to {MAX_UPLOAD_FILES} files per upload · 10 MB maximum per file"
                ).classes("text-xs").style("color: var(--ta-muted)")

            with ui.row().classes("mt-3 flex-wrap gap-2 no-wrap"):
                ui.button("Upload to current folder", icon="upload",
                          on_click=lambda: upload.run_method("upload")).classes(PRIMARY)
                ui.button("Clear selection", on_click=lambda: upload.reset()).classes(BUTTON)

            async def _on_uploaded(e):
                files = getattr(e, "files", None) or []
                if not files:
                    ui.notify("Select files to upload first.", type="info")
                    return
                if len(files) > MAX_UPLOAD_FILES:
                    ui.notify(f"Select between 1 and {MAX_UPLOAD_FILES} files.", type="warning")
                    return
                uploads = []
                try:
                    for f in files:
                        content = await f.read()
                        if len(content) > MAX_FILE_SIZE:
                            ui.notify("Each file must be 10 MB or smaller.", type="warning")
                            return
                        uploads.append((f.name, content, session.mime_for(f.name)))
                except Exception:
                    ui.notify("Upload failed. Please try again.", type="error")
                    return
                upload.reset()
                _run("upload", uploads=uploads, toast="Files uploaded.")

            # Management actions
            with ui.grid().classes("mt-5 w-full gap-4 grid-cols-1 xl:grid-cols-2"):
                with ui.column().classes("gap-2 w-full"):
                    ui.label("Create a folder here").classes("ta-label")
                    with ui.row().classes("gap-2 w-full no-wrap"):
                        folder_input = ui.input(placeholder="Folder name").props(
                            "outlined dense"
                        ).classes("flex-1")
                        ui.button("Create", icon="create_new_folder",
                                  on_click=lambda: _do_create(folder_input)).classes(BUTTON)
                with ui.column().classes("gap-2 w-full"):
                    ui.label("Rename selected item").classes("ta-label")
                    with ui.row().classes("gap-2 w-full no-wrap"):
                        rename_input = ui.input(placeholder="Select a file or folder below").props(
                            "outlined dense"
                        ).classes("flex-1")
                        ui.button("Rename", icon="edit",
                                  on_click=lambda: _do_rename(rename_input)).classes(BUTTON)

            # Selection actions
            with ui.row().classes(
                "mt-5 flex-wrap items-center gap-3 w-full"
            ).style("border-top:1px solid var(--ta-border); padding-top:1.25rem"):
                selection_label = ui.label(
                    "Select an item in the file manager to rename, delete, or download."
                ).classes("min-w-0 flex-1 text-sm").style("color: #4B5563")
                download_btn = ui.button("Download", icon="download",
                                         on_click=lambda: _do_download()).classes(BUTTON)
                delete_btn = ui.button("Delete", icon="delete",
                                       on_click=lambda: _ask_delete()).classes("ta-btn-danger")

            # Delete confirmation
            confirm_row = ui.row().classes(
                "mt-4 flex-wrap items-center gap-3 w-full"
            ).style(
                "border:1px solid #FECACA; background:#FEF2F2; border-radius:.75rem; padding:1rem"
            )
            confirm_row.set_visibility(False)
            with confirm_row:
                confirm_label = ui.label("").classes("flex-1 text-sm").style("color:#B91C1C")
                ui.button("Cancel", on_click=lambda: _cancel_delete()).classes(BUTTON)
                ui.button("Confirm delete",
                          on_click=lambda: _do_delete()).classes(
                    "inline-flex items-center justify-center gap-2 rounded-lg px-4 py-2.5 text-sm font-medium text-white"
                ).style("background:#DC2626")

        # Browser
        with ui.element("section").classes("w-full").style(
            "background:#fff; border:1px solid var(--ta-border); border-radius:1rem"
        ):
            with ui.row().classes("items-center gap-3 p-4").style(
                "border-bottom:1px solid var(--ta-border)"
            ):
                up_btn = ui.button("Up", icon="arrow_upward",
                                   on_click=lambda: _go_up()).classes(BUTTON)
                path_label = ui.label("/").classes(
                    "min-w-0 flex-1 truncate text-sm font-medium"
                ).style("color: #374151")
                ui.button("Refresh", icon="refresh",
                          on_click=lambda: _do_refresh()).classes(BUTTON)

            error_label = ui.label("").classes("m-4 rounded-lg p-3 text-sm").style(
                "background:#FEF2F2; color:#B91C1C; display:none"
            )
            busy_row = ui.row().classes(
                "items-center gap-2 px-4 py-3 text-sm"
            ).style("background:#EFF6FF; color:#1D4ED8")
            busy_spinner = ui.spinner(size="sm")
            busy_text = ui.label("Working on your files…")
            busy_row.set_visibility(False)

            empty_row = ui.column().classes(
                "items-center gap-2 px-4 py-5 w-full"
            ).style("background: var(--ta-bg)")
            with empty_row:
                ui.icon("folder_open").classes("text-2xl").style("color: var(--ta-primary)")
                ui.label("This folder is empty").classes("text-sm font-semibold").style(
                    "color: #374151"
                )
                ui.label(
                    "Upload your first file or create a folder using the actions above."
                ).classes("text-xs").style("color: var(--ta-muted)")
            empty_row.set_visibility(False)

            table = ui.table(
                columns=[
                    {"name": "name", "label": "Name", "field": "name", "align": "left"},
                    {"name": "type", "label": "Type", "field": "type", "align": "left"},
                    {"name": "size", "label": "Size", "field": "size", "align": "right"},
                    {"name": "date", "label": "Modified", "field": "date", "align": "left"},
                ],
                rows=[],
                row_key="id",
                selection="single",
            ).classes("w-full min-w-[600px]").props("flat separator=cell")

            table.add_slot("body-cell-name", r"""
                <q-td :props="props">
                    <div class="flex items-center gap-2" @click="$parent.$emit('open', props.row)" style="cursor:pointer">
                        <span>{{ props.row.type === 'folder' ? '📁' : '📄' }}</span>
                        <span class="font-medium">{{ props.row.name }}</span>
                    </div>
                </q-td>
            """)
            table.add_slot("body-cell-size", r"""
                <q-td :props="props">
                    <span style="color:#6B7280">{{ props.row.type === 'folder' ? '—' : props.row.size_label }}</span>
                </q-td>
            """)
            table.add_slot("body-cell-date", r"""
                <q-td :props="props">
                    <span style="color:#6B7280">{{ props.row.date_label }}</span>
                </q-td>
            """)

            def render():
                items = view.get("items", [])
                path_label.text = view.get("current_path", "/")
                storage_label.text = f"{session.storage_label(items)} stored"
                # Add display helpers for slots.
                rows = []
                for it in items:
                    rows.append({
                        **it,
                        "name": it["id"].rsplit("/", 1)[-1],
                        "size_label": _format_size(it["size"]),
                        "date_label": (it["date"][:19].replace("T", " ")),
                    })
                table.rows = rows
                empty_row.set_visibility(bool(view.get("loaded")) and session.folder_is_empty(items, view.get("current_path", "/")))
                # selection label
                if view.get("selected_path"):
                    selection_label.text = f"Selected: {view.get('selected_name')}"
                else:
                    selection_label.text = (
                        "Select an item in the file manager to rename, delete, or download."
                    )
                # update disabled states
                has_sel = bool(view.get("selected_path"))
                download_btn.set_enabled(has_sel and not view.get("selected_is_folder", False))
                delete_btn.set_enabled(has_sel)
                up_btn.set_enabled(view.get("current_path", "/") != "/")

            # ---- operations ----
            def _set_busy(b):
                view["busy"] = b
                busy_row.set_visibility(b)
                render()

            def _run(operation, name="", target=None, uploads=None, toast=None):
                if view["busy"]:
                    ui.notify("Please wait for the current operation.")
                    return
                target = view["current_path"] if target is None else target
                _set_busy(True)
                view["error"] = ""
                error_label.set_visibility(False)
                try:
                    metadata, next_path, dl_name, dl_bytes = session.run_file_op(
                        operation, name, target, uploads
                    )
                    view["items"] = metadata
                    view["loaded"] = True
                    if operation != "download":
                        view["current_path"] = next_path
                        view["selected_path"] = ""
                        view["selected_name"] = ""
                        view["selected_is_folder"] = False
                        view["revision"] = view.get("revision", 0) + 1
                    if operation == "download" and dl_name:
                        ui.download(dl_bytes, dl_name)
                    elif toast:
                        ui.notify(toast)
                except PermissionError:
                    session.clear_account()
                    session.clear_files_view()
                    ui.navigate.to("/auth")
                    return
                except ValueError as e:
                    view["error"] = str(e)
                    error_label.text = str(e)
                    error_label.style("display:block")
                    ui.notify(str(e), type="warning")
                except Exception:
                    view["error"] = "Unable to access your files. Please refresh and try again."
                    error_label.text = "Unable to access your files. Please refresh and try again."
                    error_label.style("display:block")
                    ui.notify("Unable to access your files.", type="error")
                finally:
                    _set_busy(False)

            def _do_create(inp):
                name = (inp.value or "").strip()
                if not name:
                    ui.notify("Enter a folder name.", type="info")
                    return
                inp.set_value("")
                _run("create", name=name, toast="Folder created.")

            def _do_rename(inp):
                if not view.get("selected_path"):
                    ui.notify("Select an item first.", type="info")
                    return
                name = (inp.value or "").strip()
                if not name:
                    ui.notify("Enter a new name.", type="info")
                    return
                _run("rename", name=name, target=view["selected_path"], toast="Item renamed.")

            def _do_download():
                if view.get("selected_path") and not view.get("selected_is_folder"):
                    _run("download", target=view["selected_path"])

            def _ask_delete():
                view["delete_confirmation"] = bool(view.get("selected_path")) and not view["busy"]
                confirm_row.set_visibility(view["delete_confirmation"])
                if view["delete_confirmation"]:
                    confirm_label.text = (
                        f"Permanently delete {view['selected_name']}? Folders and everything "
                        "inside them will be deleted. This cannot be undone."
                    )

            def _cancel_delete():
                view["delete_confirmation"] = False
                confirm_row.set_visibility(False)

            def _do_delete():
                if view["busy"] or not view["delete_confirmation"]:
                    return
                view["delete_confirmation"] = False
                confirm_row.set_visibility(False)
                _run("delete", target=view["selected_path"],
                     toast="Item deleted, including its contents.")

            def _go_up():
                cur = view.get("current_path", "/")
                view["current_path"] = cur.rsplit("/", 1)[0] or "/"
                view["selected_path"] = ""
                view["selected_name"] = ""
                view["selected_is_folder"] = False
                view["delete_confirmation"] = False
                view["revision"] = view.get("revision", 0) + 1
                _do_refresh()

            def _do_refresh():
                _run("load")

            # ---- table interactions ----
            def on_select(e):
                args = e.args if isinstance(e.args, dict) else {}
                sel = args.get("selected") or []
                if sel:
                    row = sel[0]
                    view["selected_path"] = row["id"]
                    view["selected_name"] = row["name"]
                    view["selected_is_folder"] = row["type"] == "folder"
                    view["delete_confirmation"] = False
                    confirm_row.set_visibility(False)
                else:
                    view["selected_path"] = ""
                    view["selected_name"] = ""
                    view["selected_is_folder"] = False
                render()

            def on_open(e):
                row = e.args
                if not row:
                    return
                if row.get("type") == "folder":
                    view["current_path"] = row["id"]
                    view["selected_path"] = ""
                    view["selected_name"] = ""
                    view["selected_is_folder"] = False
                    _do_refresh()

            table.on("selection", on_select)
            table.on("open", on_open)

            # initial load
            def _initial_load():
                if not view.get("loaded"):
                    _run("load")

            ui.timer(0.1, _initial_load, once=True)


def build():
    from .layout import shell

    shell("Files", files_content)