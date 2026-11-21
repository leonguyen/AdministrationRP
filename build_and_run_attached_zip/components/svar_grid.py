import reflex as rx
from reflex.components.component import NoSSRComponent
from reflex.utils.imports import ImportVar
from build_and_run_attached_zip.states.menu_state import MenuRow, MenuToolbarItem


MENU_COLUMNS: list[dict[str, str | int | bool]] = [
    {
        "id": "hierarchy_name",
        "header": "Hierarchy Name",
        "width": 280,
        "sort": True,
    },
    {"id": "sign_in_url", "header": "Sign in Url", "width": 220, "sort": True},
    {
        "id": "management_url",
        "header": "Management Url",
        "width": 300,
        "sort": True,
    },
]


def selection_id(event: rx.Var[dict[str, str]]) -> list[rx.Var[str]]:
    return [event["id"]]


class SvarGrid(NoSSRComponent):
    library = "@svar-ui/react-grid@2.7.6"
    tag = "Grid"

    data: rx.Var[list[MenuRow]]
    columns: rx.Var[list[dict[str, str | int | bool]]]
    select: rx.Var[bool]
    multiselect: rx.Var[bool]
    selected_rows: rx.Var[list[str]]
    on_select_row: rx.EventHandler[selection_id]


def toolbar_action_id(
    event: rx.Var[dict[str, MenuToolbarItem]],
) -> list[rx.Var[str]]:
    return [event["item"]["id"]]


class SvarToolbar(NoSSRComponent):
    library = "@svar-ui/react-toolbar@2.6.1"
    tag = "Toolbar"

    items: rx.Var[list[MenuToolbarItem]]
    overflow: rx.Var[str]
    on_click: rx.EventHandler[toolbar_action_id]

    def add_imports(self) -> dict[str, list[ImportVar]]:
        return {"@svar-ui/react-toolbar/all.css": [ImportVar(tag=None)]}


class Willow(rx.Component):
    library = "@svar-ui/react-grid@2.7.6"
    tag = "Willow"

    def add_imports(self) -> dict[str, list[ImportVar]]:
        return {"@svar-ui/react-grid/all.css": [ImportVar(tag=None)]}


def menu_toolbar(
    items: rx.Var[list[MenuToolbarItem]],
    on_action: rx.event.EventType,
) -> rx.Component:
    return rx.el.div(
        Willow.create(
            SvarToolbar.create(
                items=items,
                overflow="wrap",
                on_click=on_action,
            ),
            class_name="w-full min-w-0 bg-transparent font-['Inter'] text-sm text-[#1D2939] [&_button]:font-['Inter'] [&_button]:text-sm [&>div]:flex [&>div]:flex-wrap [&>div]:gap-2",
        ),
        custom_attrs={"data-testid": "svar-menu-toolbar"},
        class_name="w-full min-w-0 sm:w-auto sm:max-w-full",
    )


def menu_grid(
    data: rx.Var[list[MenuRow]],
    selected_rows: rx.Var[list[str]],
    on_select_row: rx.event.EventType,
) -> rx.Component:
    return rx.el.div(
        Willow.create(
            SvarGrid.create(
                data=data,
                columns=MENU_COLUMNS,
                select=True,
                multiselect=False,
                selected_rows=selected_rows,
                on_select_row=on_select_row,
                class_name="h-full w-full bg-white text-[#1D2939]",
            ),
            class_name="h-full w-full bg-white font-['Inter'] text-[#1D2939]",
        ),
        custom_attrs={"data-testid": "svar-menu-grid"},
        class_name="h-[500px] min-h-[500px] w-full min-w-[800px] shrink-0 bg-white font-['Inter'] text-[#1D2939] [&>div]:h-full",
    )
