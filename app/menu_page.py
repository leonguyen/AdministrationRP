"""Menu hierarchy management: searchable grid + add/edit/delete dialog.

Ported from the Reflex app's menu.py (svar grid -> NiceGUI table).
Session-only state (rows reset on reload), stored per tab in session.menu_rows().
"""
import uuid

from nicegui import ui

from .layout import page_title
from . import session


def _filtered(rows, query):
    q = query.strip().lower()
    if not q:
        return rows
    return [
        r for r in rows
        if q in r["hierarchy_name"].lower()
        or q in r["sign_in_url"].lower()
        or q in r["management_url"].lower()
    ]


def _menu_dialog(row, on_save):
    editing = row is not None
    form = dict(row) if row else {
        "id": str(uuid.uuid4()),
        "hierarchy_name": "",
        "sign_in_url": "/signin",
        "management_url": "",
        "depth": 0,
    }

    with ui.dialog() as dialog, ui.card().classes("w-full").style(
        "max-width:32rem; border-radius:1rem"
    ):
        with ui.row().classes("items-center justify-between w-full no-wrap"):
            ui.label("Edit Menu" if editing else "Add Menu").classes(
                "text-xl font-semibold"
            ).style("color: var(--ta-text)")
            ui.button(icon="close", on_click=dialog.close).props("flat dense round").style(
                "color: var(--ta-muted)"
            )
        ui.label("Define a hierarchy and its route mapping. Use / to separate levels.").classes(
            "mt-2 text-sm leading-6"
        ).style("color: var(--ta-muted)")

        name_input = ui.input("Hierarchy Name *", value=form["hierarchy_name"],
                              placeholder="e.g. Users / Profile").props("outlined dense").classes("w-full")
        signin_input = ui.input("Sign in Url", value=form["sign_in_url"],
                                placeholder="/signin").props("outlined dense").classes("w-full")
        mgmt_input = ui.input("Management Url", value=form["management_url"],
                              placeholder="/admin/...").props("outlined dense").classes("w-full")
        error_box = ui.label("").classes("text-sm").style(
            "color:#B91C1C; background:#FEF2F2; border-radius:.5rem; padding:.5rem .75rem; display:none"
        )

        def save():
            name = (name_input.value or "").strip()
            if not name:
                error_box.text = "Hierarchy name is required."
                error_box.style("display:block")
                return
            saved = {
                "id": form["id"],
                "hierarchy_name": name,
                "sign_in_url": (signin_input.value or "").strip(),
                "management_url": (mgmt_input.value or "").strip(),
                "depth": name.count("/"),
            }
            on_save(saved)
            dialog.close()

        with ui.row().classes("justify-end gap-3 w-full mt-4 pt-5").style(
            "border-top:1px solid var(--ta-border)"
        ):
            ui.button("Cancel", on_click=dialog.close).props("flat dense").classes("ta-btn")
            ui.button("Save", icon="check", on_click=save).classes("ta-btn-primary")

    return dialog


def menu_content():
    rows = session.menu_rows()
    selected = {"id": ""}

    with ui.column().classes("w-full min-w-0 gap-0"):
        page_title("Menu", "Manage menu hierarchy and route mapping.")

        with ui.row().classes("items-center justify-between w-full mb-5 no-wrap"):
            ui.label("Menu hierarchy").classes("ta-section-title")
            ui.button("Add Menu", icon="add", on_click=lambda: _open(None)).classes(
                "ta-btn-primary"
            )

        with ui.card().classes("w-full").style(
            "border-radius:1rem; border:1px solid var(--ta-border); background:#fff"
        ):
            with ui.row().classes("items-center justify-between w-full p-5").style(
                "border-bottom:1px solid var(--ta-border)"
            ):
                search = ui.input(placeholder="Search menu...").props(
                    "outlined dense"
                ).classes("w-full").style("max-width:24rem")
                count_label = ui.label().classes("text-sm").style("color: var(--ta-muted)")

            table = ui.table(
                columns=[
                    {"name": "hierarchy_name", "label": "Hierarchy Name",
                     "field": "hierarchy_name", "align": "left", "sortable": True},
                    {"name": "sign_in_url", "label": "Sign in Url",
                     "field": "sign_in_url", "align": "left", "sortable": True},
                    {"name": "management_url", "label": "Management Url",
                     "field": "management_url", "align": "left", "sortable": True},
                    {"name": "actions", "label": "Actions", "field": "actions", "align": "right"},
                ],
                rows=[],
                row_key="id",
                selection="single",
            ).classes("w-full min-w-[800px]").props("flat separator=cell")

            table.add_slot("body-cell-hierarchy_name", r"""
                <q-td :props="props">
                    <span class="font-medium" :style="'padding-left:' + (props.row.depth || 0) * 20 + 'px'">
                        <span v-if="props.row.depth > 0" style="color:#9CA3AF;margin-right:6px">›</span>
                        {{ props.row.hierarchy_name }}
                    </span>
                </q-td>
            """)
            table.add_slot("body-cell-sign_in_url", r"""
                <q-td :props="props">
                    <span style="font-family:monospace;font-size:.8rem;color:#6B7280">{{ props.row.sign_in_url }}</span>
                </q-td>
            """)
            table.add_slot("body-cell-management_url", r"""
                <q-td :props="props">
                    <span style="font-family:monospace;font-size:.8rem;color:#6B7280">{{ props.row.management_url }}</span>
                </q-td>
            """)
            table.add_slot("body-cell-actions", r"""
                <q-td :props="props">
                    <div class="flex justify-end gap-1">
                        <button class="ta-icon-btn" @click="$parent.$emit('edit', props.row.id)" title="Edit">✏️</button>
                        <button class="ta-icon-btn danger" @click="$parent.$emit('delete', props.row.id)" title="Delete">🗑️</button>
                    </div>
                </q-td>
            """)

            def refresh():
                data = _filtered(rows, search.value or "")
                count_label.text = f"{len(data)} items"
                table.rows = data
                if selected["id"] and not any(r["id"] == selected["id"] for r in data):
                    selected["id"] = ""

            def on_edit(row_id):
                row = next((r for r in rows if r["id"] == row_id), None)
                if row:
                    _open(row)

            def on_delete(row_id):
                rows[:] = [r for r in rows if r["id"] != row_id]
                if selected["id"] == row_id:
                    selected["id"] = ""
                refresh()
                ui.notify("Menu deleted.")

            def _open(row):
                def save(saved):
                    for i, r in enumerate(rows):
                        if r["id"] == saved["id"]:
                            rows[i] = saved
                            break
                    else:
                        rows.append(saved)
                    refresh()
                    ui.notify("Menu saved. Changes are kept for this session only.")

                _menu_dialog(row, save).open()

            def on_select(e):
                args = e.args if isinstance(e.args, dict) else {}
                sel = args.get("selected") or []
                selected["id"] = sel[0]["id"] if sel else ""

            table.on("selection", on_select)
            table.on("edit", lambda e: on_edit(e.args))
            table.on("delete", lambda e: on_delete(e.args))

            search.on_value_change(lambda _: refresh())
            refresh()

            with ui.row().classes("items-center justify-between w-full p-4").style(
                "border-top:1px solid var(--ta-border)"
            ):
                ui.label("")
                with ui.row().classes("gap-2 no-wrap"):
                    ui.button("Edit selected", icon="edit", on_click=lambda: _guard(on_edit)).props(
                        "flat dense"
                    ).style("color: var(--ta-text)")
                    ui.button("Delete selected", icon="delete", on_click=lambda: _guard(on_delete)).props(
                        "flat dense"
                    ).style("color: var(--ta-text)")

                def _guard(fn):
                    if selected["id"]:
                        fn(selected["id"])
                    else:
                        ui.notify("Select a row first.", type="info")

        ui.label("Changes are kept in this session only and reset on reload. URLs are route mappings, not active navigation links.").classes(
            "mt-5 flex items-start gap-2 text-xs leading-5"
        ).style("color: var(--ta-muted)")


def build():
    from .layout import shell

    shell("Menu", menu_content)