"""Local email/password authentication service.

Ported from the Reflex app's LocalAuthState. Framework-agnostic: pure functions
over the database, using argon2 for password hashing, email normalization, and
account lockout (5 failed attempts -> 15 minute lock).
"""
import logging
import re
import secrets
from contextlib import suppress
from datetime import UTC, datetime, timedelta

from argon2 import PasswordHasher, Type
from argon2.exceptions import (
    InvalidHashError,
    VerificationError,
    VerifyMismatchError,
)
from sqlalchemy import select

from .db import session
from .models import LocalAccount

MAX_FAILED_ATTEMPTS = 5
LOCK_MINUTES = 15


def _hasher() -> PasswordHasher:
    return PasswordHasher(time_cost=2, memory_cost=19456, parallelism=2, type=Type.ID)


def normalize_email(value: str) -> str:
    email = value.strip().lower()
    if len(email) > 254 or not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email):
        raise ValueError("Enter a valid email address.")
    return email


def get_profile(account_id: str) -> tuple[str, str, str]:
    """Return (id, email, display_name) for an account, or ("","","") if missing."""
    if not account_id:
        return "", "", ""
    with session() as db:
        row = db.execute(
            select(
                LocalAccount.id,
                LocalAccount.email,
                LocalAccount.display_name,
            ).where(LocalAccount.id == account_id)
        ).first()
        return (row.id, row.email, row.display_name or "") if row else ("", "", "")


def authenticate(
    email: str, password: str, confirmation: str, signup: bool
) -> tuple[str, str, str]:
    """Sign in or register. Returns (id, email, display_name).

    Raises ValueError with a user-safe message on failure.
    """
    email = normalize_email(email)
    if len(password) > 1024:
        raise ValueError("Password must be at most 1024 characters.")
    if signup and (len(password) < 12 or password != confirmation):
        raise ValueError(
            "Use at least 12 characters and make sure both passwords match."
        )
    hasher = _hasher()
    with session() as db:
        account = db.scalar(
            select(LocalAccount)
            .where(LocalAccount.email == email)
            .with_for_update()
        )
        if signup:
            if account:
                raise ValueError(
                    "Unable to create this account. Try signing in instead."
                )
            account = LocalAccount(email=email, password_hash=hasher.hash(password))
            db.add(account)
            try:
                db.flush()
                result = (account.id, account.email, account.display_name or "")
                return result
            except Exception:
                raise ValueError(
                    "Unable to create this account. Try signing in instead."
                ) from None
        failure = "Unable to sign in. Check your credentials or try again later."
        now = datetime.now(UTC)
        if account is None:
            # Do comparable password work for unknown accounts.
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
            logging.exception("Unexpected error verifying password")
            valid = False
        if not valid:
            account.failed_attempts += 1
            if account.failed_attempts >= MAX_FAILED_ATTEMPTS:
                account.locked_until = now + timedelta(minutes=LOCK_MINUTES)
            # Persist the failed-attempt counter even though sign-in failed.
            db.commit()
            raise ValueError(failure)
        if hasher.check_needs_rehash(account.password_hash):
            account.password_hash = hasher.hash(password)
        account.failed_attempts = 0
        account.locked_until = None
        account.last_login_at = now
        result = (account.id, account.email, account.display_name or "")
        db.commit()
        return result