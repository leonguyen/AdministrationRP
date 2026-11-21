import reflex as rx
import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class AuthenticationGuards(unittest.TestCase):
    def test_sign_in_plugin_and_auth_only_routes_are_removed(self):
        config = (ROOT / "rxconfig.py").read_text()
        app_source = (ROOT / "app" / "app.py").read_text()
        sources = [path.read_text() for path in (ROOT / "app").rglob("*.py")]
        self.assertNotIn("AuthPlugin", config)
        self.assertNotIn("reflex_enterprise.auth", "\n".join(sources))
        self.assertNotIn("auth=", "\n".join(sources))
        self.assertNotIn("/login", "\n".join(sources))
        self.assertIn('route="/"', app_source)
        self.assertTrue(callable(rx.Component))


if __name__ == "__main__":
    unittest.main()
