"""Initial menu hierarchy rows (session-only, ported from menu_state.py)."""

from typing import TypedDict


class MenuRow(TypedDict):
    id: str
    hierarchy_name: str
    sign_in_url: str
    management_url: str
    depth: int


def initial_rows() -> list[MenuRow]:
    return [
        {"id": "1", "hierarchy_name": "Dashboard", "sign_in_url": "/signin", "management_url": "/admin/dashboard", "depth": 0},
        {"id": "2", "hierarchy_name": "Dashboard / Ecommerce", "sign_in_url": "/signin", "management_url": "/admin/dashboard/ecommerce", "depth": 1},
        {"id": "3", "hierarchy_name": "Dashboard / Analytics", "sign_in_url": "/signin", "management_url": "/admin/dashboard/analytics", "depth": 1},
        {"id": "4", "hierarchy_name": "Users", "sign_in_url": "/signin", "management_url": "/admin/users", "depth": 0},
        {"id": "5", "hierarchy_name": "Users / Profile", "sign_in_url": "/signin", "management_url": "/admin/users/profile", "depth": 1},
        {"id": "6", "hierarchy_name": "Users / Roles", "sign_in_url": "/signin", "management_url": "/admin/users/roles", "depth": 1},
        {"id": "7", "hierarchy_name": "Settings", "sign_in_url": "/signin", "management_url": "/admin/settings", "depth": 0},
        {"id": "8", "hierarchy_name": "Settings / Billing", "sign_in_url": "/signin", "management_url": "/admin/settings/billing", "depth": 1},
    ]