import reflex as rx

import asyncio
import logging
import re
import secrets
from contextlib import suppress
from datetime import UTC, datetime, timedelta
from typing import Any

from argon2 import PasswordHasher, Type
from argon2.exceptions import (
    InvalidHashError,
    VerificationError,
    VerifyMismatchError,
)
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from build_and_run_attached_zip.models import LocalAccount


class LocalAuthState(rx.State):
    _account_id: str = ""
    _session_revision: int = 0
    _form_revision: int = 0
    _email: str = ""
    _name: str = ""
    opened: bool = False
    mode: str = "sign_in"
    error: str = ""
    submitting: bool = False

    @rx.var
    def is_authenticated(self) -> bool:
        return bool(self._account_id)

    @rx.var
    def email(self) -> str:
        return self._email if self._account_id else ""

    @rx.var
    def display_name(self) -> str:
        return (self._name or self._email) if self._account_id else ""

    @staticmethod
    def _hasher() -> PasswordHasher:
        return PasswordHasher(
            time_cost=2, memory_cost=19456, parallelism=2, type=Type.ID
        )

    @staticmethod
    def _normalize_email(value: str) -> str:
        email = value.strip().lower()
        if len(email) > 254 or not re.fullmatch(
            r"[^\s@]+@[^\s@]+\.[^\s@]+", email
        ):
            raise ValueError("Enter a valid email address.")
        return email

    @staticmethod
    def _profile(account_id: str) -> tuple[str, str, str]:
        if not account_id:
            return "", "", ""
        with rx.session() as session:
            row = session.execute(
                select(
                    LocalAccount.id,
                    LocalAccount.email,
                    LocalAccount.display_name,
                ).where(LocalAccount.id == account_id)
            ).first()
            return (
                (row.id, row.email, row.display_name or "")
                if row
                else ("", "", "")
            )

    @staticmethod
    def _authenticate(
        email: str, password: str, confirmation: str, signup: bool
    ) -> tuple[str, str, str]:
        email = LocalAuthState._normalize_email(email)
        if len(password) > 1024:
            raise ValueError("Password must be at most 1024 characters.")
        if signup and (len(password) < 12 or password != confirmation):
            raise ValueError(
                "Use at least 12 characters and make sure both passwords match."
            )
        hasher = LocalAuthState._hasher()
        with rx.session() as session:
            account = session.scalar(
                select(LocalAccount)
                .where(LocalAccount.email == email)
                .with_for_update()
            )
            if signup:
                if account:
                    raise ValueError(
                        "Unable to create this account. Try signing in instead."
                    )
                account = LocalAccount(
                    email=email, password_hash=hasher.hash(password)
                )
                session.add(account)
                try:
                    session.flush()
                    result = (
                        account.id,
                        account.email,
                        account.display_name or "",
                    )
                    session.commit()
                except IntegrityError:
                    session.rollback()
                    raise ValueError(
                        "Unable to create this account. Try signing in instead."
                    ) from None
                return result
            failure = (
                "Unable to sign in. Check your credentials or try again later."
            )
            now = datetime.now(UTC)
            if account is None:
                # Do comparable password work for unknown accounts without persisting credentials.
                hasher.hash(secrets.token_urlsafe(32))
                raise ValueError(failure)
            locked = account.locked_until
            if locked and locked.tzinfo is None:
                locked = locked.replace(tzinfo=UTC)
            if locked and locked > now:
                raise ValueError(failure)
            if locked:
                account.failed_attempts = 0
                account.locked_until = None
            valid = False
            try:
                with suppress(VerifyMismatchError):
                    valid = hasher.verify(account.password_hash, password)
            except (VerificationError, InvalidHashError):
                logging.exception("Unexpected error")
                valid = False
            if not valid:
                account.failed_attempts += 1
                if account.failed_attempts >= 5:
                    account.locked_until = now + timedelta(minutes=15)
                session.commit()
                raise ValueError(failure)
            if hasher.check_needs_rehash(account.password_hash):
                account.password_hash = hasher.hash(password)
            account.failed_attempts = 0
            account.locked_until = None
            account.last_login_at = now
            result = (account.id, account.email, account.display_name or "")
            session.commit()
            return result

    def _clear_identity(self):
        self._account_id = ""
        self._email = ""
        self._name = ""
        self._session_revision += 1

    async def _clear_files(self):
        from build_and_run_attached_zip.states.files_state import FilesState

        files = await self.get_state(FilesState)
        files._clear_private_view()

    async def _validate_identity(self) -> bool:
        account_id = self._account_id
        revision = self._session_revision
        try:
            profile = await asyncio.to_thread(self._profile, account_id)
        except Exception as e:
            logging.exception(
                f"Error: account validation failed ({type(e).__name__})"
            )
            profile = ("", "", "")
        if revision != self._session_revision:
            return False
        if not profile[0]:
            self._clear_identity()
            await self._clear_files()
            return False
        self._email, self._name = profile[1], profile[2]
        return True

    @rx.event
    async def guard_account(self):
        if not await self._validate_identity():
            return rx.redirect("/auth")

    @rx.event
    async def refresh_identity(self):
        await self._validate_identity()

    @rx.event
    async def auth_entry(self):
        if await self._validate_identity():
            yield rx.redirect("/account")
        else:
            yield LocalAuthState.open_sign_up

    @rx.event
    def open_sign_in(self):
        self.mode = "sign_in"
        self.opened = True
        self.error = ""
        self._form_revision += 1

    @rx.event
    def open_sign_up(self):
        self.mode = "sign_up"
        self.opened = True
        self.error = ""
        self._form_revision += 1

    @rx.event
    def close_modal(self):
        self.opened = False
        self.error = ""
        self._form_revision += 1

    @rx.event(background=True)
    async def sign_in(self, form_data: dict[str, Any]):
        async with self:
            pass
        async for event in self._submit(form_data, False):
            yield event

    @rx.event(background=True)
    async def register(self, form_data: dict[str, Any]):
        async with self:
            pass
        async for event in self._submit(form_data, True):
            yield event

    async def _submit(self, form_data: dict[str, Any], signup: bool):
        async with self:
            if self.submitting:
                return
            self.submitting = True
            self.error = ""
            revision = self._session_revision
            form_revision = self._form_revision
        try:
            profile = await asyncio.to_thread(
                self._authenticate,
                str(form_data.get("email", "")),
                str(form_data.get("password", "")),
                str(form_data.get("confirm_password", "")),
                signup,
            )
            form_data.clear()
            async with self:
                if (
                    revision != self._session_revision
                    or form_revision != self._form_revision
                ):
                    return
                await self._clear_files()
                self._account_id, self._email, self._name = profile
                self._session_revision += 1
                self.opened = False
                self.error = ""
            yield rx.redirect("/account")
        except ValueError as e:
            async with self:
                if form_revision == self._form_revision:
                    self.error = (
                        str(e)
                        if signup
                        else "Unable to sign in. Check your credentials or try again later."
                    )
        except Exception as e:
            logging.exception(
                f"Error: authentication failed ({type(e).__name__})",
                exc_info=(
                    RuntimeError,
                    RuntimeError(
                        "Account access failed; credential details suppressed."
                    ),
                    None,
                ),
            )
            async with self:
                if form_revision == self._form_revision:
                    self.error = "Account access is temporarily unavailable. Please try again."
        finally:
            form_data.clear()
            async with self:
                self.submitting = False

    @rx.event
    async def logout(self):
        self._clear_identity()
        self._form_revision += 1
        self.opened = False
        self.error = ""
        await self._clear_files()
        return [
            rx.clear_selected_files("persistent-files-upload"),
            rx.redirect("/"),
        ]
