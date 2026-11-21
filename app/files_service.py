"""File storage service: folders, uploads, rename, delete, download.

Ported from the Reflex app's FilesState. Framework-agnostic functions over the
database. Each account has a private namespace (owner_sub = "local:<id>").
For SQLite (which lacks pg advisory locks) we serialize writes per-owner with a
process-local lock.
"""
import logging
import mimetypes
import re
import threading
import unicodedata
from datetime import UTC, datetime
from typing import TypedDict

from sqlalchemy import select
from sqlalchemy.orm import defer

from .db import session
from .models import FileItem, LocalAccount

MAX_FILE_SIZE = 10 * 1024 * 1024
MAX_UPLOAD_FILES = 5

# Serialize writes per owner within this process (SQLite-friendly replacement
# for pg_advisory_xact_lock).
_locks: dict[str, threading.Lock] = {}
_locks_guard = threading.Lock()


def _owner_lock(owner: str) -> threading.Lock:
    with _locks_guard:
        return _locks.setdefault(owner, threading.Lock())


class FileEntry(TypedDict):
    id: str
    type: str
    size: int
    date: str


def safe_name(raw: str) -> str:
    name = unicodedata.normalize("NFC", raw.replace("\\", "/").rsplit("/", 1)[-1])
    name = (
        re.sub(r'[\x00-\x1f\x7f<>:"|?*]', "_", name).strip().strip(".").strip()
    )
    if not name or name in {".", ".."} or len(name.encode("utf-8")) > 255:
        raise ValueError(
            "Use a name between 1 and 255 UTF-8 bytes, without path separators."
        )
    return name


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


def _perform(
    account_id: str,
    operation: str,
    target: str,
    name: str,
    uploads: list[tuple[str, bytes, str]],
) -> tuple[list[FileEntry], str, str, bytes]:
    """Core DB operation. Returns (metadata, next_path, download_name, download_bytes)."""
    if not account_id:
        raise PermissionError("Sign in to access your files.")
    with session() as db:
        account = db.scalar(
            select(LocalAccount.id)
            .where(LocalAccount.id == account_id)
            .with_for_update()
        )
        if not account:
            raise PermissionError("Sign in to access your files.")
        owner = f"local:{account}"

        rows = list(
            db.scalars(
                select(FileItem)
                .where(FileItem.owner_sub == owner)
                .options(defer(FileItem.content))
            ).all()
        )
        paths = _paths(rows)
        selected = paths.get(target)
        folder = None if target == "/" else selected
        download_name = ""
        download_bytes = b""
        next_path = target

        if operation in {"create", "upload"}:
            if target != "/" and (folder is None or not folder.is_folder):
                raise ValueError(
                    "This folder is no longer available. Refresh your files."
                )
            parent_id = folder.id if folder else None
            sibling_names = {
                row.name.casefold()
                for row in rows
                if row.parent_id == parent_id
            }
            batch = uploads if operation == "upload" else [(name, b"", "")]
            for raw_name, content, mime in batch:
                safe = safe_name(raw_name)
                if safe.casefold() in sibling_names:
                    raise ValueError(
                        "An item with that name already exists in this folder."
                    )
                if len(content) > MAX_FILE_SIZE:
                    raise ValueError("Each file must be 10 MB or smaller.")
                sibling_names.add(safe.casefold())
                db.add(
                    FileItem(
                        owner_sub=owner,
                        parent_id=parent_id,
                        name=safe,
                        is_folder=operation == "create",
                        size=len(content),
                        content=content if operation == "upload" else None,
                        mime_type=mime if operation == "upload" else None,
                    )
                )
        elif operation in {"rename", "delete", "download"}:
            if selected is None:
                raise ValueError("Select an available item first.")
            if operation == "rename":
                safe = safe_name(name)
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
                    db.delete(row)
                    db.flush()
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

        db.flush()
        refreshed = list(
            db.scalars(
                select(FileItem)
                .where(FileItem.owner_sub == owner)
                .options(defer(FileItem.content))
            ).all()
        )
        refreshed_paths = _paths(refreshed)
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
        return metadata, next_path, download_name, download_bytes


def execute(
    account_id: str,
    operation: str,
    name: str,
    target: str,
    uploads: list[tuple[str, bytes, str]] | None = None,
) -> tuple[list[FileEntry], str, str, bytes]:
    """Public entry point: serializes writes per owner, then runs _perform."""
    if not account_id:
        raise PermissionError("Sign in to access your files.")
    owner = f"local:{account_id}"
    with _owner_lock(owner):
        return _perform(
            account_id, operation, target, name, uploads or []
        )


def mime_for(name: str) -> str:
    return mimetypes.guess_type(name)[0] or "application/octet-stream"