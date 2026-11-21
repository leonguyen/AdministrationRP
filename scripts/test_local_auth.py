import reflex as rx

import ast
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from argon2 import Type
from argon2.exceptions import (
    InvalidHashError,
    VerificationError,
    VerifyMismatchError,
)
from sqlalchemy.exc import IntegrityError

from build_and_run_attached_zip.components.account import account_profile
from build_and_run_attached_zip.components.account_access import (
    MantineModal,
    account_access_strip,
    sign_in_content,
    sign_up_content,
)
from build_and_run_attached_zip.components.files import files_page
from build_and_run_attached_zip.components.hosting_footer import MantineProvider
from build_and_run_attached_zip.models import LocalAccount
from build_and_run_attached_zip.states.files_state import FilesState
from build_and_run_attached_zip.states.local_auth_state import LocalAuthState


class LocalAuthTests(unittest.TestCase):
    def test_email_normalization(self):
        self.assertEqual(
            LocalAuthState._normalize_email("  Person@Example.COM  "),
            "person@example.com",
        )
        for value in ("", "bad", "a@b", "a b@example.com"):
            with self.assertRaises(ValueError):
                LocalAuthState._normalize_email(value)

    def test_argon2id(self):
        hasher = LocalAuthState._hasher()
        self.assertEqual(hasher.type, Type.ID)
        password = "a-long-test-password-not-a-credential"
        digest = hasher.hash(password)
        self.assertTrue(hasher.verify(digest, password))
        with self.assertRaises(VerifyMismatchError):
            hasher.verify(digest, "incorrect")

    def test_signup_validation_precedes_database(self):
        with patch("app.states.local_auth_state.rx.session") as factory:
            for password, confirmation in (
                ("short", "short"),
                ("long-test-password", "different"),
            ):
                with self.assertRaises(ValueError):
                    LocalAuthState._authenticate(
                        "test@example.com", password, confirmation, True
                    )
            factory.assert_not_called()

    def test_invalid_login_increments_database_lockout(self):
        account = LocalAccount(
            id="test-id",
            email="test@example.com",
            password_hash=LocalAuthState._hasher().hash("valid-test-password"),
            failed_attempts=4,
            locked_until=None,
        )
        session = MagicMock()
        session.scalar.return_value = account
        with (
            patch("app.states.local_auth_state.rx.session") as factory,
            patch("app.states.local_auth_state.logging.exception") as log,
        ):
            factory.return_value.__enter__.return_value = session
            with self.assertRaises(ValueError) as failure:
                LocalAuthState._authenticate(account.email, "wrong", "", False)
            self.assertEqual(
                str(failure.exception),
                "Unable to sign in. Check your credentials or try again later.",
            )
            log.assert_not_called()
        self.assertEqual(account.failed_attempts, 5)
        self.assertIsNotNone(account.locked_until)
        session.commit.assert_called_once()

    def test_corrupted_hash_uses_generic_failure_and_database_lockout(self):
        for error in (
            InvalidHashError("invalid hash"),
            VerificationError("invalid encoding"),
        ):
            with self.subTest(error=type(error).__name__):
                account = LocalAccount(
                    id="test-id",
                    email="test@example.com",
                    password_hash="corrupted-hash",
                    failed_attempts=4,
                    locked_until=None,
                )
                session = MagicMock()
                session.scalar.return_value = account
                hasher = MagicMock()
                hasher.verify.side_effect = error
                with (
                    patch("app.states.local_auth_state.rx.session") as factory,
                    patch.object(
                        LocalAuthState, "_hasher", return_value=hasher
                    ),
                    patch(
                        "app.states.local_auth_state.logging.exception"
                    ) as log,
                ):
                    factory.return_value.__enter__.return_value = session
                    with self.assertRaises(ValueError) as failure:
                        LocalAuthState._authenticate(
                            account.email, "wrong", "", False
                        )
                    self.assertEqual(
                        str(failure.exception),
                        "Unable to sign in. Check your credentials or try again later.",
                    )
                    log.assert_called_once()
                self.assertEqual(account.failed_attempts, 5)
                self.assertIsNotNone(account.locked_until)
                session.commit.assert_called_once()
                hasher.check_needs_rehash.assert_not_called()

    def test_account_route_guard_keeps_auth_public(self):
        path = Path(__file__).resolve().parents[1] / "app/app.py"
        tree = ast.parse(path.read_text())
        routes = {}
        for node in tree.body:
            if not isinstance(node, ast.Expr) or not isinstance(
                node.value, ast.Call
            ):
                continue
            call = node.value
            if (
                not isinstance(call.func, ast.Attribute)
                or call.func.attr != "add_page"
            ):
                continue
            keywords = {keyword.arg: keyword.value for keyword in call.keywords}
            route = keywords.get("route")
            if isinstance(route, ast.Constant):
                routes[route.value] = ast.unparse(keywords["on_load"])
        self.assertIn("LocalAuthState.guard_account", routes["/account"])
        for route, on_load in routes.items():
            if route != "/account":
                self.assertNotIn("LocalAuthState.guard_account", on_load)
        self.assertEqual(
            routes["/auth"],
            "[ShellState.close_mobile, HostingState.load_metrics]",
        )

    def test_locked_account_cannot_sign_in(self):
        from datetime import UTC, datetime, timedelta

        account = LocalAccount(
            id="test-id",
            email="test@example.com",
            password_hash="",
            failed_attempts=5,
            locked_until=datetime.now(UTC) + timedelta(minutes=15),
        )
        session = MagicMock()
        session.scalar.return_value = account
        with patch("app.states.local_auth_state.rx.session") as factory:
            factory.return_value.__enter__.return_value = session
            with self.assertRaisesRegex(ValueError, "Unable to sign in"):
                LocalAuthState._authenticate(
                    account.email, "anything", "", False
                )
        session.commit.assert_not_called()

    def test_signup_unique_constraint_race_rolls_back(self):
        session = MagicMock()
        session.scalar.return_value = None
        session.flush.side_effect = IntegrityError(
            "insert", {}, Exception("duplicate")
        )
        with patch("app.states.local_auth_state.rx.session") as factory:
            factory.return_value.__enter__.return_value = session
            with self.assertRaisesRegex(ValueError, "Unable to create"):
                LocalAuthState._authenticate(
                    "test@example.com",
                    "long-test-password",
                    "long-test-password",
                    True,
                )
        session.rollback.assert_called_once()
        session.commit.assert_not_called()

    def test_database_refuses_unverified_identity(self):
        with self.assertRaises(PermissionError):
            FilesState._database("", "load", "/", "", [])
        session = MagicMock()
        session.scalar.return_value = None
        with patch("app.states.files_state.rx.session") as factory:
            factory.return_value.__enter__.return_value = session
            with self.assertRaises(PermissionError):
                FilesState._database("local", "delete", "/private", "", [])
        session.execute.assert_not_called()
        session.commit.assert_not_called()

    def test_modal_forms_and_guarded_pages_construct(self):
        for component in (
            account_access_strip(),
            sign_in_content(),
            sign_up_content(),
            account_profile(),
            files_page(),
        ):
            self.assertIsInstance(component, rx.Component)
        self.assertIn("confirm_password", str(sign_up_content()))
        self.assertIn("current-password", str(sign_in_content()))
        self.assertEqual(MantineModal.library, "@mantine/core@7.17.8")
        self.assertIn(
            "@mantine/core/styles.css", MantineProvider.create()._get_imports()
        )
        self.assertIn("Sign in required", str(files_page()))
        self.assertIn("Sign in required", str(account_profile()))

    def test_no_password_state_fields_or_identity_setter(self):
        path = (
            Path(__file__).resolve().parents[1]
            / "app/states/local_auth_state.py"
        )
        tree = ast.parse(path.read_text())
        state = next(
            node for node in tree.body if isinstance(node, ast.ClassDef)
        )
        fields = [
            node.target.id
            for node in state.body
            if isinstance(node, ast.AnnAssign)
        ]
        self.assertIn("_account_id", fields)
        self.assertFalse(any("password" in field for field in fields))
        self.assertNotIn("set_account_id", LocalAuthState.event_handlers)


if __name__ == "__main__":
    unittest.main()
