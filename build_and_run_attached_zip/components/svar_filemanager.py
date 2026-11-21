import reflex as rx
from reflex.components.component import NoSSRComponent
from reflex.utils.imports import ImportVar

from build_and_run_attached_zip.states.files_state import FileEntry, FilePanel, FilesState


def action_id(event: rx.Var[dict[str, str]]) -> list[rx.Var[str]]:
    return [event.get("id", "")]


class Filemanager(NoSSRComponent):
    library = "@svar-ui/react-filemanager@2.6.0"
    tag = "Filemanager"
    data: rx.Var[list[FileEntry]]
    drive: rx.Var[dict[str, int]]
    panels: rx.Var[list[FilePanel]]
    mode: rx.Var[str]
    readonly: rx.Var[bool]
    menu_options: rx.Var[str]
    on_set_path: rx.EventHandler[action_id]
    on_select_file: rx.EventHandler[action_id]
    on_download_file: rx.EventHandler[action_id]


class FileWillow(NoSSRComponent):
    library = "@svar-ui/react-filemanager@2.6.0"
    tag = "Willow"
    alias = "FileWillow"

    def add_imports(self) -> dict[str, list[ImportVar]]:
        return {"@svar-ui/react-filemanager/all.css": [ImportVar(tag=None)]}


def filemanager_panel() -> rx.Component:
    return rx.el.div(
        FileWillow.create(
            Filemanager.create(
                data=rx.Var(
                    f"({FilesState.items}).map(item => ({{...item, date: new Date(item.date)}}))",
                    _var_type=list[FileEntry],
                    _var_data=FilesState.items._var_data,
                ),
                drive=FilesState.drive,
                panels=FilesState.panels,
                mode="table",
                readonly=True,
                menu_options=rx.Var("(() => [])", _var_type=str),
                on_set_path=FilesState.set_path,
                on_select_file=FilesState.select_file,
                on_download_file=FilesState.download_path,
                key=FilesState.revision,
                class_name="h-full w-full bg-white text-[#1D2939]",
            ),
            class_name="h-full w-full bg-white font-['Inter'] text-[#1D2939] [&>div]:h-full",
        ),
        custom_attrs={"data-testid": "svar-filemanager"},
        class_name="h-[560px] min-h-[560px] min-w-[780px] w-full shrink-0 bg-white [&>div]:h-full",
    )
