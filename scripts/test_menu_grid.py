import reflex as rx
import argparse
import json
import unittest
from build_and_run_attached_zip.components.menu import menu_page
from build_and_run_attached_zip.components.svar_grid import (
    MENU_COLUMNS,
    SvarGrid,
    SvarToolbar,
    Willow,
    toolbar_action_id,
)
from build_and_run_attached_zip.states.menu_state import MenuState, initial_rows


class MenuGridTests(unittest.TestCase):
    def test_component_construction(self):
        page = menu_page()
        self.assertIsInstance(page, rx.Component)
        self.assertIn("svar-menu-grid", str(page))
        grid = SvarGrid.create(
            data=initial_rows(),
            columns=MENU_COLUMNS,
            select=True,
            multiselect=False,
            selected_rows=[],
            on_select_row=MenuState.select_row,
        )
        self.assertEqual(grid.library, "@svar-ui/react-grid@2.7.6")
        self.assertEqual(grid.tag, "Grid")
        self.assertIn("onSelectRow", grid.render()["props"].__str__())
        self.assertIn(
            "@svar-ui/react-grid/all.css", Willow.create().add_imports()
        )

    def test_toolbar_component_and_payload(self):
        state = MenuState(_init=True)
        toolbar = SvarToolbar.create(
            items=state.toolbar_items,
            overflow="wrap",
            on_click=MenuState.toolbar_action,
        )
        self.assertEqual(toolbar.library, "@svar-ui/react-toolbar@2.6.1")
        self.assertEqual(toolbar.tag, "Toolbar")
        self.assertIn("onClick", str(toolbar.render()["props"]))
        self.assertIn("@svar-ui/react-toolbar/all.css", toolbar.add_imports())
        self.assertIn("svar-menu-toolbar", str(menu_page()))
        payload = rx.Var.create({"item": state.toolbar_items[0]})
        reduced = toolbar_action_id(payload)
        self.assertEqual(len(reduced), 1)
        self.assertIn('"id"', str(reduced[0]))
        self.assertNotIn('"text"', str(reduced[0]).split("]")[-1])

    def test_toolbar_items_follow_selection(self):
        state = MenuState(_init=True)
        items = state.toolbar_items
        self.assertEqual(
            [item["id"] for item in items],
            ["edit-selected", "delete-selected", "add-menu"],
        )
        self.assertEqual(
            [item["icon"] for item in items],
            ["wxi-pencil", "wxi-trash", "wxi-plus"],
        )
        self.assertTrue(all(item["comp"] == "button" for item in items))
        self.assertEqual(
            [item["disabled"] for item in items], [True, True, False]
        )
        self.assertEqual(json.loads(json.dumps(items)), items)
        self.assertTrue(all("handler" not in item for item in items))
        state.selected_id = "2"
        self.assertEqual(
            [item["disabled"] for item in state.toolbar_items],
            [False, False, False],
        )
        state.query = "no matching menu"
        state._reconcile_selection()
        self.assertEqual(state.selected_id, "")
        self.assertEqual(
            [item["disabled"] for item in state.toolbar_items],
            [True, True, False],
        )

    def test_toolbar_dispatches_existing_events(self):
        for action_id, handler in (
            ("edit-selected", MenuState.edit_selected),
            ("delete-selected", MenuState.delete_selected),
            ("add-menu", MenuState.start_create),
        ):
            self.assertEqual(
                list(MenuState.toolbar_action.fn(None, action_id)), [handler]
            )
        self.assertEqual(list(MenuState.toolbar_action.fn(None, "unknown")), [])

    def test_columns_and_stable_ids(self):
        self.assertEqual(
            [column["width"] for column in MENU_COLUMNS], [280, 220, 300]
        )
        self.assertTrue(all(column["sort"] for column in MENU_COLUMNS))
        self.assertTrue(all("editor" not in column for column in MENU_COLUMNS))
        rows = initial_rows()
        self.assertTrue(all(isinstance(row["id"], str) for row in rows))
        self.assertEqual(len({row["id"] for row in rows}), len(rows))


def check_browser(url: str):
    from playwright.sync_api import sync_playwright

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1280, "height": 900})
        errors: list[str] = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(f"{url.rstrip('/')}/menu")
        grid = page.get_by_test_id("svar-menu-grid")
        grid.wait_for(state="visible")
        page.get_by_text("Hierarchy Name", exact=True).wait_for()
        page.get_by_text("Dashboard / Ecommerce", exact=True).wait_for()
        assert grid.locator('[class*="wx-"]').count() > 0, "SVAR DOM missing"
        assert grid.bounding_box()["height"] == 500
        toolbar = page.get_by_test_id("svar-menu-toolbar")
        toolbar.wait_for(state="visible")
        assert toolbar.locator('[class*="wx-"]').count() > 0, (
            "SVAR Toolbar DOM missing"
        )
        assert toolbar.get_by_role("button").count() == 3
        for icon in ("wxi-pencil", "wxi-trash", "wxi-plus"):
            assert toolbar.locator(f".{icon}").count() == 1
        edit = toolbar.get_by_role("button", name="Edit selected", exact=True)
        delete = toolbar.get_by_role(
            "button", name="Delete selected", exact=True
        )
        add = toolbar.get_by_role("button", name="Add Menu", exact=True)
        assert add.is_enabled()
        assert edit.is_disabled() and delete.is_disabled()
        page.get_by_text("Dashboard / Ecommerce", exact=True).click()
        edit.wait_for()
        page.wait_for_function(
            "() => !Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('Edit selected')).disabled"
        )
        edit.click()
        page.get_by_label("Hierarchy Name").fill("Grid verification / Edited")
        page.get_by_role("button", name="Save", exact=True).click()
        page.get_by_text("Grid verification / Edited", exact=True).wait_for()
        page.get_by_label("Search menu", exact=True).fill("Grid verification")
        page.get_by_text("1 items", exact=True).wait_for()
        page.get_by_text("Grid verification / Edited", exact=True).click()
        delete.click()
        page.get_by_text("No menus found", exact=True).wait_for()
        assert edit.is_disabled() and delete.is_disabled()
        assert add.is_enabled()
        page.get_by_role("button", name="Clear menu search").click()
        add.click()
        page.get_by_label("Hierarchy Name").fill("Grid verification / Created")
        page.get_by_label("Management Url").fill("/grid-verification")
        page.get_by_role("button", name="Save", exact=True).click()
        page.get_by_text("Grid verification / Created", exact=True).wait_for()
        page.set_viewport_size({"width": 390, "height": 844})
        page.wait_for_function(
            "() => { const grid = document.querySelector('[data-testid=\"svar-menu-grid\"]'); return grid.parentElement.scrollWidth > grid.parentElement.clientWidth; }"
        )
        toolbar.scroll_into_view_if_needed()
        bounds = toolbar.bounding_box()
        assert (
            bounds and bounds["x"] >= 0 and bounds["x"] + bounds["width"] <= 391
        )
        for button in (edit, delete, add):
            box = button.bounding_box()
            assert box and box["x"] >= 0 and box["x"] + box["width"] <= 391
        add.click()
        page.get_by_label("Hierarchy Name").wait_for(state="visible")
        page.get_by_role("button", name="Cancel", exact=True).click()
        assert not errors, errors
        browser.close()
        print(
            "Actual SVAR Grid and Toolbar rendering, icons, disabled states, toolbar edit/delete/create wiring, search and mobile wrapping passed."
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="")
    args = parser.parse_args()
    if args.url:
        check_browser(args.url)
    else:
        unittest.main(argv=["test_menu_grid"])
