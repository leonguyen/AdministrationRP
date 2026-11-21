import reflex as rx
import ast
import unittest
from pathlib import Path
from build_and_run_attached_zip.states.menu_state import initial_rows
from build_and_run_attached_zip.components.dashboard import SALES_DATA, STATS_DATA


class AppGuards(unittest.TestCase):
    def test_source_menu(self):
        rows = initial_rows()
        self.assertEqual(len(rows), 8)
        for row in rows:
            self.assertEqual(row["depth"], row["hierarchy_name"].count("/"))
            self.assertEqual(row["sign_in_url"], "/signin")
        self.assertEqual(rows[-1]["management_url"], "/admin/settings/billing")

    def test_chart_values(self):
        self.assertEqual(
            SALES_DATA["value"],
            [168, 385, 201, 298, 187, 195, 291, 110, 215, 390, 280, 112],
        )
        self.assertEqual(
            STATS_DATA["sales"],
            [180, 190, 170, 175, 160, 172, 170, 200, 225, 240, 235, 230],
        )
        self.assertEqual(
            STATS_DATA["revenue"],
            [40, 30, 50, 45, 80, 95, 100, 120, 135, 150, 155, 140],
        )

    def test_no_external_account_actions(self):
        root = Path(__file__).resolve().parents[1] / "app"
        for file in root.rglob("*.py"):
            tree = ast.parse(file.read_text())
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    self.assertFalse(
                        any(
                            item.name.startswith(
                                ("supabase", "requests", "httpx")
                            )
                            for item in node.names
                        )
                    )
                if isinstance(node, ast.ImportFrom):
                    self.assertFalse(
                        (node.module or "").startswith(
                            ("supabase", "requests", "httpx")
                        )
                    )
        self.assertTrue(callable(rx.App))


if __name__ == "__main__":
    unittest.main()
