import reflex as rx
from typing import Any, TypedDict
from uuid import uuid4


class MenuToolbarItem(TypedDict):
    id: str
    comp: str
    text: str
    icon: str
    disabled: bool
    css: str


class MenuRow(TypedDict):
    id: str
    hierarchy_name: str
    sign_in_url: str
    management_url: str
    depth: int


def initial_rows() -> list[MenuRow]:
    return [
        {
            "id": "1",
            "hierarchy_name": "Dashboard",
            "sign_in_url": "/signin",
            "management_url": "/admin/dashboard",
            "depth": 0,
        },
        {
            "id": "2",
            "hierarchy_name": "Dashboard / Ecommerce",
            "sign_in_url": "/signin",
            "management_url": "/admin/dashboard/ecommerce",
            "depth": 1,
        },
        {
            "id": "3",
            "hierarchy_name": "Dashboard / Analytics",
            "sign_in_url": "/signin",
            "management_url": "/admin/dashboard/analytics",
            "depth": 1,
        },
        {
            "id": "4",
            "hierarchy_name": "Users",
            "sign_in_url": "/signin",
            "management_url": "/admin/users",
            "depth": 0,
        },
        {
            "id": "5",
            "hierarchy_name": "Users / Profile",
            "sign_in_url": "/signin",
            "management_url": "/admin/users/profile",
            "depth": 1,
        },
        {
            "id": "6",
            "hierarchy_name": "Users / Roles",
            "sign_in_url": "/signin",
            "management_url": "/admin/users/roles",
            "depth": 1,
        },
        {
            "id": "7",
            "hierarchy_name": "Settings",
            "sign_in_url": "/signin",
            "management_url": "/admin/settings",
            "depth": 0,
        },
        {
            "id": "8",
            "hierarchy_name": "Settings / Billing",
            "sign_in_url": "/signin",
            "management_url": "/admin/settings/billing",
            "depth": 1,
        },
    ]


class MenuState(rx.State):
    rows: list[MenuRow] = initial_rows()
    query: str = ""
    selected_id: str = ""
    modal_open: bool = False
    editing_id: str = ""
    hierarchy_name: str = ""
    sign_in_url: str = "/signin"
    management_url: str = ""
    error: str = ""

    @rx.var
    def filtered_rows(self) -> list[MenuRow]:
        query = self.query.strip().lower()
        return [
            row
            for row in self.rows
            if any(
                query in row[field].lower()
                for field in ("hierarchy_name", "sign_in_url", "management_url")
            )
        ]

    @rx.var
    def selected_rows(self) -> list[str]:
        return [self.selected_id] if self.selected_id else []

    @rx.var
    def toolbar_items(self) -> list[MenuToolbarItem]:
        return [
            {
                "id": "edit-selected",
                "comp": "button",
                "text": "Edit selected",
                "icon": "wxi-pencil",
                "disabled": self.selected_id == "",
                "css": "rounded-lg! bg-white! text-[#1D2939]! focus-visible:ring-2 focus-visible:ring-[#465FFF]",
            },
            {
                "id": "delete-selected",
                "comp": "button",
                "text": "Delete selected",
                "icon": "wxi-trash",
                "disabled": self.selected_id == "",
                "css": "rounded-lg! bg-white! text-[#1D2939]! focus-visible:ring-2 focus-visible:ring-[#465FFF]",
            },
            {
                "id": "add-menu",
                "comp": "button",
                "text": "Add Menu",
                "icon": "wxi-plus",
                "disabled": False,
                "css": "rounded-lg! bg-[#465FFF]! text-white! hover:bg-[#3641D9]! focus-visible:ring-2 focus-visible:ring-[#465FFF] focus-visible:ring-offset-2",
            },
        ]

    @rx.event
    def toolbar_action(self, action_id: str):
        match action_id:
            case "edit-selected":
                yield MenuState.edit_selected
            case "delete-selected":
                yield MenuState.delete_selected
            case "add-menu":
                yield MenuState.start_create

    def _reconcile_selection(self):
        if not any(row["id"] == self.selected_id for row in self.filtered_rows):
            self.selected_id = ""

    @rx.event
    def select_row(self, row_id: str):
        self.selected_id = row_id
        self._reconcile_selection()

    @rx.event
    def edit_selected(self):
        self._reconcile_selection()
        if self.selected_id:
            yield MenuState.start_edit(self.selected_id)

    @rx.event
    def delete_selected(self):
        self._reconcile_selection()
        if self.selected_id:
            yield MenuState.delete_menu(self.selected_id)

    @rx.event
    def set_query(self, value: str):
        self.query = value
        self._reconcile_selection()

    @rx.event
    def clear_search(self):
        self.query = ""

    @rx.event
    def start_create(self):
        self.editing_id = ""
        self.hierarchy_name = ""
        self.sign_in_url = "/signin"
        self.management_url = ""
        self.error = ""
        self.modal_open = True

    @rx.event
    def start_edit(self, row_id: str):
        row = next((row for row in self.rows if row["id"] == row_id), None)
        if row:
            self.editing_id = row_id
            self.hierarchy_name = row["hierarchy_name"]
            self.sign_in_url = row["sign_in_url"]
            self.management_url = row["management_url"]
            self.error = ""
            self.modal_open = True

    @rx.event
    def change_modal(self, opened: bool):
        self.modal_open = opened
        self.error = ""

    @rx.event
    def close_modal(self):
        self.modal_open = False
        self.error = ""

    @rx.event
    def save_menu(self, form_data: dict[str, Any]):
        name = str(form_data.get("hierarchy_name", "")).strip()
        if not name:
            self.error = "Hierarchy name is required."
            return
        row: MenuRow = {
            "id": self.editing_id or str(uuid4()),
            "hierarchy_name": name,
            "sign_in_url": str(form_data.get("sign_in_url", "")).strip(),
            "management_url": str(form_data.get("management_url", "")).strip(),
            "depth": name.count("/"),
        }
        if self.editing_id:
            self.rows = [
                row if item["id"] == self.editing_id else item
                for item in self.rows
            ]
        else:
            self.rows = [*self.rows, row]
        self._reconcile_selection()
        self.modal_open = False
        self.error = ""
        return rx.toast("Menu saved. Changes are kept for this session only.")

    @rx.event
    def delete_menu(self, row_id: str):
        self.rows = [row for row in self.rows if row["id"] != row_id]
        self._reconcile_selection()
        return rx.toast("Menu deleted.")
