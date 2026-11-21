import reflex as rx

from build_and_run_attached_zip.components.shell import page_title
from build_and_run_attached_zip.components.svar_filemanager import filemanager_panel
from build_and_run_attached_zip.states.files_state import FilesState, MAX_FILE_SIZE
from build_and_run_attached_zip.states.local_auth_state import LocalAuthState
from build_and_run_attached_zip.components.account import login_required


BUTTON = "inline-flex items-center justify-center gap-2 rounded-lg border border-gray-200 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:cursor-not-allowed disabled:opacity-50 focus-visible:ring-2 focus-visible:ring-[#465FFF]"
PRIMARY = "inline-flex items-center justify-center gap-2 rounded-lg bg-[#465FFF] px-4 py-2.5 text-sm font-medium text-white hover:bg-[#364CE0] disabled:cursor-not-allowed disabled:opacity-50 focus-visible:ring-2 focus-visible:ring-[#465FFF]"
INPUT = "w-full rounded-lg border border-gray-200 bg-white px-3 py-2.5 text-sm text-gray-700 focus:border-[#465FFF] focus:outline-hidden focus:ring-2 focus:ring-[#465FFF]/20"


def upload_area() -> rx.Component:
    return rx.el.div(
        rx.upload.root(
            rx.icon("cloud-upload", class_name="h-7 w-7 text-[#465FFF]"),
            rx.el.p(
                "Click to choose files, or drag them here",
                class_name="text-sm font-medium text-gray-700",
            ),
            rx.el.p(
                "Up to 5 files per upload · 10 MB maximum per file",
                class_name="text-xs text-gray-500",
            ),
            id="persistent-files-upload",
            multiple=True,
            max_size=MAX_FILE_SIZE,
            max_files=5,
            disabled=FilesState.busy,
            class_name="flex w-full cursor-pointer flex-col items-center gap-2 rounded-xl border border-dashed border-gray-300 bg-[#F9FAFB] p-5 text-gray-700 focus-within:ring-2 focus-within:ring-[#465FFF]",
        ),
        rx.el.div(
            rx.foreach(
                rx.selected_files("persistent-files-upload"),
                lambda name: rx.el.span(
                    name,
                    class_name="max-w-full truncate rounded-md bg-gray-100 px-2 py-1 text-xs text-gray-700",
                ),
            ),
            class_name="mt-3 flex flex-wrap gap-2",
        ),
        rx.el.div(
            rx.el.button(
                rx.icon("upload", class_name="h-4 w-4"),
                "Upload to current folder",
                on_click=FilesState.handle_upload(
                    rx.upload_files(upload_id="persistent-files-upload")
                ),
                disabled=FilesState.busy
                | (rx.selected_files("persistent-files-upload").length() == 0)
                | ~FilesState.loaded,
                class_name=PRIMARY,
            ),
            rx.el.button(
                "Clear selection",
                on_click=rx.clear_selected_files("persistent-files-upload"),
                disabled=FilesState.busy,
                class_name=BUTTON,
            ),
            class_name="mt-3 flex flex-wrap gap-2",
        ),
        class_name="w-full",
    )


def management_actions() -> rx.Component:
    return rx.el.div(
        rx.el.form(
            rx.el.label(
                "Create a folder here",
                html_for="files-folder-name",
                class_name="mb-2 block text-sm font-medium text-gray-700",
            ),
            rx.el.div(
                rx.el.input(
                    id="files-folder-name",
                    name="folder_name",
                    placeholder="Folder name",
                    required=True,
                    max_length=255,
                    class_name=INPUT,
                ),
                rx.el.button(
                    rx.icon("folder-plus", class_name="h-4 w-4"),
                    "Create",
                    type="submit",
                    disabled=FilesState.busy | ~FilesState.loaded,
                    class_name=BUTTON,
                ),
                class_name="flex gap-2",
            ),
            on_submit=FilesState.create_folder,
            reset_on_submit=True,
            class_name="w-full",
        ),
        rx.el.form(
            rx.el.label(
                "Rename selected item",
                html_for="files-new-name",
                class_name="mb-2 block text-sm font-medium text-gray-700",
            ),
            rx.el.div(
                rx.el.input(
                    id="files-new-name",
                    name="new_name",
                    default_value=FilesState.selected_name,
                    key=FilesState.selected_name,
                    placeholder="Select a file or folder below",
                    required=True,
                    max_length=255,
                    disabled=FilesState.selected_path == "",
                    class_name=INPUT,
                ),
                rx.el.button(
                    rx.icon("pencil", class_name="h-4 w-4"),
                    "Rename",
                    type="submit",
                    disabled=FilesState.busy | (FilesState.selected_path == ""),
                    class_name=BUTTON,
                ),
                class_name="flex gap-2",
            ),
            on_submit=FilesState.rename_selected,
            class_name="w-full",
        ),
        class_name="mt-5 grid w-full grid-cols-1 gap-4 xl:grid-cols-2",
    )


def selection_actions() -> rx.Component:
    return rx.el.div(
        rx.el.p(
            rx.cond(
                FilesState.selected_path != "",
                f"Selected: {FilesState.selected_name}",
                "Select an item in the file manager to rename, delete, or download.",
            ),
            class_name="min-w-0 flex-1 truncate text-sm text-gray-600",
        ),
        rx.el.button(
            rx.icon("download", class_name="h-4 w-4"),
            "Download",
            on_click=FilesState.download_selected,
            disabled=FilesState.busy
            | (FilesState.selected_path == "")
            | FilesState.selected_is_folder,
            class_name=BUTTON,
        ),
        rx.el.button(
            rx.icon("trash-2", class_name="h-4 w-4"),
            "Delete",
            on_click=FilesState.ask_delete,
            disabled=FilesState.busy | (FilesState.selected_path == ""),
            class_name="inline-flex items-center gap-2 rounded-lg border border-red-200 bg-white px-4 py-2.5 text-sm font-medium text-red-600 hover:bg-red-50 disabled:opacity-50 focus-visible:ring-2 focus-visible:ring-red-500",
        ),
        class_name="mt-5 flex flex-wrap items-center gap-3 border-t border-gray-200 pt-5",
    )


def files_page() -> rx.Component:
    return rx.cond(
        LocalAuthState.is_authenticated, private_files_page(), login_required()
    )


def private_files_page() -> rx.Component:
    return rx.el.div(
        page_title("Files", "Your private workspace for files and folders."),
        rx.el.section(
            rx.el.div(
                rx.el.div(
                    rx.icon("hard-drive", class_name="h-5 w-5 text-[#465FFF]"),
                    rx.el.h2(
                        "My files",
                        class_name="text-lg font-semibold text-[#1D2939]",
                    ),
                    class_name="flex items-center gap-2",
                ),
                rx.el.span(
                    f"{FilesState.storage_label} stored",
                    class_name="w-fit rounded-full bg-gray-100 px-3 py-1 text-xs font-medium text-gray-600",
                ),
                class_name="mb-4 flex items-center justify-between gap-3",
            ),
            rx.el.p(
                "Persistent storage belongs to your signed-in account only. Files are saved across reloads. Duplicate names within a folder are not allowed.",
                class_name="mb-5 text-sm leading-6 text-gray-500",
            ),
            upload_area(),
            management_actions(),
            selection_actions(),
            rx.cond(
                FilesState.delete_confirmation,
                rx.el.div(
                    rx.el.p(
                        f"Permanently delete {FilesState.selected_name}? Folders and everything inside them will be deleted. This cannot be undone.",
                        class_name="flex-1 text-sm text-red-700",
                    ),
                    rx.el.button(
                        "Cancel",
                        on_click=FilesState.cancel_delete,
                        class_name=BUTTON,
                    ),
                    rx.el.button(
                        "Confirm delete",
                        on_click=FilesState.delete_selected,
                        class_name="rounded-lg bg-red-600 px-4 py-2.5 text-sm font-medium text-white hover:bg-red-700 focus-visible:ring-2 focus-visible:ring-red-500",
                    ),
                    role="alert",
                    class_name="mt-4 flex flex-wrap items-center gap-3 rounded-xl border border-red-200 bg-red-50 p-4",
                ),
            ),
            class_name="mb-6 w-full rounded-2xl border border-gray-200 bg-white p-5 lg:p-6",
        ),
        rx.el.section(
            rx.el.div(
                rx.el.button(
                    rx.icon("arrow-up", class_name="h-4 w-4"),
                    "Up",
                    on_click=FilesState.go_up,
                    disabled=(FilesState.current_path == "/") | FilesState.busy,
                    class_name=BUTTON,
                ),
                rx.el.p(
                    FilesState.current_path,
                    class_name="min-w-0 flex-1 truncate text-sm font-medium text-gray-700",
                ),
                rx.el.button(
                    rx.icon("refresh-cw", class_name="h-4 w-4"),
                    "Refresh",
                    on_click=FilesState.load,
                    disabled=FilesState.busy,
                    class_name=BUTTON,
                ),
                class_name="flex items-center gap-3 border-b border-gray-200 p-4",
            ),
            rx.cond(
                FilesState.error != "",
                rx.el.p(
                    FilesState.error,
                    role="alert",
                    class_name="m-4 rounded-lg bg-red-50 p-3 text-sm text-red-700",
                ),
            ),
            rx.cond(
                FilesState.busy,
                rx.el.div(
                    rx.icon("loader-circle", class_name="h-4 w-4 animate-spin"),
                    "Working on your files…",
                    role="status",
                    class_name="flex items-center gap-2 border-b border-gray-200 bg-blue-50 px-4 py-3 text-sm text-blue-700",
                ),
            ),
            rx.cond(
                FilesState.folder_empty,
                rx.el.div(
                    rx.icon("folder-open", class_name="h-6 w-6 text-[#465FFF]"),
                    rx.el.p(
                        "This folder is empty",
                        class_name="text-sm font-semibold text-gray-700",
                    ),
                    rx.el.p(
                        "Upload your first file or create a folder using the actions above.",
                        class_name="text-xs text-gray-500",
                    ),
                    class_name="flex flex-col items-center gap-2 border-b border-gray-200 bg-[#F9FAFB] px-4 py-5",
                ),
            ),
            rx.cond(
                FilesState.loaded,
                rx.el.div(
                    filemanager_panel(), class_name="w-full overflow-x-auto"
                ),
                rx.el.div(
                    class_name="m-5 h-[560px] w-auto animate-pulse rounded-xl bg-gray-100"
                ),
            ),
            class_name="w-full rounded-2xl border border-gray-200 bg-white",
        ),
        class_name="w-full min-w-0",
    )
