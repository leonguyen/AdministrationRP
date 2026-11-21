import reflex as rx

import asyncio
import logging
import mimetypes
import re
import unicodedata
from datetime import UTC, datetime
from typing import Any, TypedDict

from sqlalchemy import select, text
from sqlalchemy.orm import defer

from build_and_run_attached_zip.models import FileItem, LocalAccount


MAX_FILE_SIZE = 10 * 1024 * 1024
MAX_UPLOAD_FILES = 5


class FileEntry(TypedDict):
    id: str
    type: str
    size: int
    date: str


class FilePanel(TypedDict):
    path: str
    selected: list[str]


class FilesState(rx.State):
    items: list[FileEntry] = []
    current_path: str = "/"
    selected_path: str = ""
    selected_name: str = ""
    selected_is_folder: bool = False
    busy: bool = False
    loaded: bool = False
    error: str = ""
    revision: int = 0
    delete_confirmation: bool = False
    _pending_uploads: list[tuple[str, bytes, str]] = []
    _view_revision: int = 0

    def _clear_private_view(self):
        self.items = []
        self.current_path = "/"
        self.selected_path = ""
        self.selected_name = ""
        self.selected_is_folder = False
        self.busy = False
        self.loaded = False
        self.error = ""
        self.delete_confirmation = False
        self._pending_uploads = []
        self._view_revision += 1
        self.revision += 1

    async def _verified_account(self) -> str:
        from build_and_run_attached_zip.states.local_auth_state import LocalAuthState

        auth = await self.get_state(LocalAuthState)
        if not await auth._validate_identity():
            self._clear_private_view()
            return ""
        return auth._account_id

    @rx.var
    def drive(self) -> dict[str, int]:
        used = sum(
            item["size"] for item in self.items if item["type"] == "file"
        )
        return {"used": used, "total": used}

    @rx.var
    def panels(self) -> list[FilePanel]:
        return [
            {
                "path": self.current_path,
                "selected": [self.selected_path] if self.selected_path else [],
            }
        ]

    @rx.var
    def storage_label(self) -> str:
        used = self.drive["used"]
        if used >= 1024 * 1024:
            return f"{used / (1024 * 1024):.2f} MB"
        if used >= 1024:
            return f"{used / 1024:.2f} KB"
        return f"{used} B"

    @rx.var
    def folder_empty(self) -> bool:
        return self.loaded and not any(
            item["id"].rsplit("/", 1)[0] == self.current_path.rstrip("/")
            for item in self.items
        )

    @staticmethod
    def _safe_name(raw: str) -> str:
        name = unicodedata.normalize(
            "NFC", raw.replace("\\", "/").rsplit("/", 1)[-1]
        )
        name = (
            re.sub(r'[\x00-\x1f\x7f<>:"|?*]', "_", name)
            .strip()
            .strip(".")
            .strip()
        )
        if not name or name in {".", ".."} or len(name.encode("utf-8")) > 255:
            raise ValueError(
                "Use a name between 1 and 255 UTF-8 bytes, without path separators."
            )
        return name

    @staticmethod
    def _paths(rows: list[FileItem]) -> dict[str, FileItem]:
        by_id = {row.id: row for row in rows}
        paths: dict[str, str] = {}
        visiting: set[str] = set()

        def resolve(row: FileItem) -> str:
            if row.id in paths:
                return paths[row.id]
            if row.id in visiting:
                raise ValueError("The folder hierarchy needs repair.")
            visiting.add(row.id)
            parent = by_id.get(row.parent_id) if row.parent_id else None
            if row.parent_id and (parent is None or not parent.is_folder):
                raise ValueError("The folder hierarchy needs repair.")
            prefix = resolve(parent) if parent else ""
            paths[row.id] = f"{prefix}/{row.name}"
            visiting.remove(row.id)
            return paths[row.id]

        return {resolve(row): row for row in rows}

    @staticmethod
    def _database(
        account_id: str,
        operation: str,
        target: str,
        name: str,
        uploads: list[tuple[str, bytes, str]],
    ) -> tuple[list[FileEntry], str, str, bytes]:
        if not account_id:
            raise PermissionError("Sign in to access your files.")
        with rx.session() as session:
            try:
                account = session.scalar(
                    select(LocalAccount.id)
                    .where(LocalAccount.id == account_id)
                    .with_for_update()
                )
                if not account:
                    raise PermissionError("Sign in to access your files.")
                owner = f"local:{account}"
                # Serialize writes per owner, including duplicate checks in empty folders.
                session.execute(
                    text(
                        "SELECT pg_advisory_xact_lock(hashtextextended(:owner, 0))"
                    ),
                    {"owner": owner},
                )
                rows = list(
                    session.scalars(
                        select(FileItem)
                        .where(FileItem.owner_sub == owner)
                        .options(defer(FileItem.content))
                    ).all()
                )
                paths = FilesState._paths(rows)
                selected = paths.get(target)
                folder = None if target == "/" else selected
                download_name = ""
                download_bytes = b""
                next_path = target

                if operation in {"create", "upload"}:
                    if target != "/" and (
                        folder is None or not folder.is_folder
                    ):
                        raise ValueError(
                            "This folder is no longer available. Refresh your files."
                        )
                    parent_id = folder.id if folder else None
                    sibling_names = {
                        row.name.casefold()
                        for row in rows
                        if row.parent_id == parent_id
                    }
                    batch = (
                        uploads if operation == "upload" else [(name, b"", "")]
                    )
                    for raw_name, content, mime in batch:
                        safe = FilesState._safe_name(raw_name)
                        if safe.casefold() in sibling_names:
                            raise ValueError(
                                "An item with that name already exists in this folder."
                            )
                        if len(content) > MAX_FILE_SIZE:
                            raise ValueError(
                                "Each file must be 10 MB or smaller."
                            )
                        sibling_names.add(safe.casefold())
                        session.add(
                            FileItem(
                                owner_sub=owner,
                                parent_id=parent_id,
                                name=safe,
                                is_folder=operation == "create",
                                size=len(content),
                                content=content
                                if operation == "upload"
                                else None,
                                mime_type=mime
                                if operation == "upload"
                                else None,
                            )
                        )
                elif operation in {"rename", "delete", "download"}:
                    if selected is None:
                        raise ValueError("Select an available item first.")
                    if operation == "rename":
                        safe = FilesState._safe_name(name)
                        if any(
                            row.id != selected.id
                            and row.parent_id == selected.parent_id
                            and row.name.casefold() == safe.casefold()
                            for row in rows
                        ):
                            raise ValueError(
                                "An item with that name already exists in this folder."
                            )
                        selected.name = safe
                        selected.modified_at = datetime.now(UTC)
                        next_path = target.rsplit("/", 1)[0] or "/"
                    elif operation == "delete":
                        descendants = [
                            (path, row)
                            for path, row in paths.items()
                            if path == target or path.startswith(f"{target}/")
                        ]
                        for path, row in sorted(
                            descendants,
                            key=lambda item: item[0].count("/"),
                            reverse=True,
                        ):
                            session.delete(row)
                            session.flush()
                        next_path = target.rsplit("/", 1)[0] or "/"
                    else:
                        if selected.is_folder:
                            raise ValueError(
                                "Select a file to download. Folder downloads are not supported."
                            )
                        download_name = selected.name
                        download_bytes = bytes(selected.content or b"")
                elif operation != "load":
                    raise ValueError("Unsupported file action.")

                session.flush()
                refreshed = list(
                    session.scalars(
                        select(FileItem)
                        .where(FileItem.owner_sub == owner)
                        .options(defer(FileItem.content))
                    ).all()
                )
                refreshed_paths = FilesState._paths(refreshed)
                metadata: list[FileEntry] = [
                    {
                        "id": path,
                        "type": "folder" if row.is_folder else "file",
                        "size": row.size,
                        "date": row.modified_at.isoformat(),
                    }
                    for path, row in sorted(refreshed_paths.items())
                ]
                if (
                    operation == "load"
                    and next_path != "/"
                    and (
                        next_path not in refreshed_paths
                        or not refreshed_paths[next_path].is_folder
                    )
                ):
                    next_path = "/"
                session.commit()
                return metadata, next_path, download_name, download_bytes
            except Exception:
                session.rollback()
                raise

    @rx.event
    async def load(self):
        if not await self._verified_account():
            yield rx.redirect("/auth")
            return
        if self.busy:
            return
        self.busy = True
        self.loaded = False
        self.items = []
        self.selected_path = ""
        self.selected_name = ""
        self.delete_confirmation = False
        yield FilesState.execute("load", "", self.current_path)

    @rx.event
    async def set_path(self, path: str):
        if not await self._verified_account():
            return rx.redirect("/auth")
        if self.busy:
            return
        if path == "/" or any(
            item["id"] == path and item["type"] == "folder"
            for item in self.items
        ):
            self.current_path = path
            self.selected_path = ""
            self.selected_name = ""
            self.selected_is_folder = False
            self.delete_confirmation = False

    @rx.event
    async def select_file(self, path: str):
        if not await self._verified_account():
            return rx.redirect("/auth")
        if self.busy:
            return
        item = next((item for item in self.items if item["id"] == path), None)
        self.selected_path = path if item else ""
        self.selected_name = path.rsplit("/", 1)[-1] if item else ""
        self.selected_is_folder = bool(item and item["type"] == "folder")
        self.delete_confirmation = False

    @rx.event
    async def create_folder(self, form_data: dict[str, Any]):
        if not await self._verified_account():
            yield rx.redirect("/auth")
            return
        if self.busy:
            return
        self.busy = True
        yield FilesState.execute(
            "create", str(form_data.get("folder_name", "")), self.current_path
        )

    @rx.event
    async def rename_selected(self, form_data: dict[str, Any]):
        if not await self._verified_account():
            yield rx.redirect("/auth")
            return
        if self.busy:
            return
        self.busy = True
        yield FilesState.execute(
            "rename", str(form_data.get("new_name", "")), self.selected_path
        )

    @rx.event
    async def ask_delete(self):
        if not await self._verified_account():
            return rx.redirect("/auth")
        self.delete_confirmation = bool(self.selected_path) and not self.busy

    @rx.event
    async def cancel_delete(self):
        if not await self._verified_account():
            return rx.redirect("/auth")
        self.delete_confirmation = False

    @rx.event
    async def delete_selected(self):
        if not await self._verified_account():
            yield rx.redirect("/auth")
            return
        if self.busy or not self.delete_confirmation:
            return
        self.busy = True
        self.delete_confirmation = False
        yield FilesState.execute("delete", "", self.selected_path)

    @rx.event
    async def download_selected(self):
        if not await self._verified_account():
            yield rx.redirect("/auth")
            return
        if self.busy:
            return
        self.busy = True
        yield FilesState.execute("download", "", self.selected_path)

    @rx.event
    async def download_path(self, path: str):
        if not await self._verified_account():
            yield rx.redirect("/auth")
            return
        if self.busy:
            return
        self.busy = True
        yield FilesState.execute("download", "", path)

    @rx.event
    async def go_up(self):
        if not await self._verified_account():
            return rx.redirect("/auth")
        if self.busy:
            return
        self.current_path = self.current_path.rsplit("/", 1)[0] or "/"
        self.selected_path = ""
        self.selected_name = ""
        self.selected_is_folder = False
        self.delete_confirmation = False
        self.revision += 1

    @rx.event
    async def handle_upload(self, files: list[rx.UploadFile]):
        if not await self._verified_account():
            yield rx.clear_selected_files("persistent-files-upload")
            yield rx.redirect("/auth")
            return
        if self.busy:
            yield rx.toast("Please wait for the current operation.")
            return
        self.busy = True
        self._pending_uploads = []
        try:
            if not files or len(files) > MAX_UPLOAD_FILES:
                raise ValueError("Select between 1 and 5 files per upload.")
            for file in files:
                safe = self._safe_name(file.name or "")
                content = await file.read(MAX_FILE_SIZE + 1)
                if len(content) > MAX_FILE_SIZE:
                    raise ValueError(
                        "Each file must be 10 MB or smaller. Nothing was saved."
                    )
                mime = (
                    mimetypes.guess_type(safe)[0] or "application/octet-stream"
                )
                self._pending_uploads.append((safe, content, mime))
        except Exception as e:
            logging.exception(f"Error: {e}")
            self._pending_uploads = []
            self.busy = False
            yield rx.toast(
                str(e)
                if isinstance(e, ValueError)
                else "Upload failed. Please try again."
            )
            return
        yield FilesState.execute("upload", "", self.current_path)

    @rx.event(background=True)
    async def execute(self, operation: str, name: str, target: str):
        from build_and_run_attached_zip.states.local_auth_state import LocalAuthState

        async with self:
            auth = await self.get_state(LocalAuthState)
            account_id = auth._account_id
            session_revision = auth._session_revision
            view_revision = self._view_revision
            uploads = (
                list(self._pending_uploads) if operation == "upload" else []
            )
            self._pending_uploads = []
            self.error = ""
        try:
            if not account_id:
                raise PermissionError("Sign in to access your files.")
            (
                metadata,
                next_path,
                download_name,
                download_bytes,
            ) = await asyncio.to_thread(
                self._database, account_id, operation, target, name, uploads
            )
            profile = await asyncio.to_thread(
                LocalAuthState._profile, account_id
            )
            async with self:
                auth = await self.get_state(LocalAuthState)
                if (
                    auth._account_id != account_id
                    or auth._session_revision != session_revision
                    or self._view_revision != view_revision
                ):
                    return
                if not profile[0]:
                    auth._clear_identity()
                    self._clear_private_view()
                    return
                self.items = metadata
                self.loaded = True
                if operation != "download":
                    self.current_path = next_path
                    self.selected_path = ""
                    self.selected_name = ""
                    self.selected_is_folder = False
                    self.revision += 1
            if operation == "download":
                yield rx.download(data=download_bytes, filename=download_name)
            elif operation != "load":
                yield rx.toast(
                    {
                        "create": "Folder created.",
                        "upload": "Files uploaded.",
                        "rename": "Item renamed.",
                        "delete": "Item deleted, including its contents.",
                    }[operation]
                )
                if operation == "upload":
                    yield rx.clear_selected_files("persistent-files-upload")
        except Exception as e:
            logging.exception(f"Error: {e}")
            message = (
                str(e)
                if isinstance(e, ValueError)
                else "Unable to access your files. Please refresh and try again."
            )
            async with self:
                auth = await self.get_state(LocalAuthState)
                if (
                    auth._session_revision != session_revision
                    or self._view_revision != view_revision
                ):
                    return
                if isinstance(e, PermissionError):
                    auth._clear_identity()
                    self._clear_private_view()
                    message = "Sign in to access your files."
                self.error = message
            yield rx.toast(message)
            if isinstance(e, PermissionError):
                yield rx.redirect("/auth")
        finally:
            async with self:
                if self._view_revision == view_revision:
                    self.busy = False
