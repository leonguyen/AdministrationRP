"""SQLAlchemy models for the TailAdmin NiceGUI app.

Ported from the Reflex app's models.py (Postgres -> SQLite compatible).
"""
from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    LargeBinary,
    String,
    Text,
    func,
    text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class FileItem(Base):
    __tablename__ = "file_items"
    __table_args__ = (
        Index("ix_file_items_owner_parent", "owner_sub", "parent_id"),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    owner_sub: Mapped[str] = mapped_column(
        Text, nullable=False, index=True, default="", server_default=""
    )
    parent_id: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("file_items.id"),
        nullable=True,
        index=True,
        default=None,
    )
    name: Mapped[str] = mapped_column(
        Text, nullable=False, default="", server_default=""
    )
    is_folder: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=text("false")
    )
    mime_type: Mapped[str | None] = mapped_column(
        Text, nullable=True, default=None
    )
    size: Mapped[int] = mapped_column(
        BigInteger, nullable=False, default=0, server_default=text("0")
    )
    content: Mapped[bytes | None] = mapped_column(
        LargeBinary, nullable=True, default=None
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
    )
    modified_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
        onupdate=lambda: datetime.now(UTC),
    )


class LocalAccount(Base):
    __tablename__ = "local_accounts"
    __table_args__ = (
        CheckConstraint(
            "email = lower(trim(email))",
            name="ck_local_accounts_email_normalized",
        ),
    )

    id: Mapped[str] = mapped_column(
        String(36), primary_key=True, default=lambda: str(uuid4())
    )
    email: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        unique=True,
        index=True,
        default="",
        server_default="",
    )
    password_hash: Mapped[str] = mapped_column(
        Text, nullable=False, default="", server_default=""
    )
    display_name: Mapped[str | None] = mapped_column(
        Text, nullable=True, default=None
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        server_default=func.now(),
    )
    failed_attempts: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default=text("0")
    )
    locked_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )