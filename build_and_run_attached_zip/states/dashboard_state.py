import reflex as rx
import logging
import re
import zipfile
from pathlib import Path
from typing import TypedDict


class TargetContent(TypedDict):
    progress: float
    percentage: str
    delta: str
    description: str
    target: str
    revenue: str
    today: str


def source_target() -> TargetContent:
    result: TargetContent = {
        "progress": 0.0,
        "percentage": "",
        "delta": "",
        "description": "",
        "target": "",
        "revenue": "",
        "today": "",
    }
    try:
        archive = (
            Path(__file__).resolve().parents[2]
            / "assets"
            / "Administration-main.zip"
        )
        with zipfile.ZipFile(archive) as bundle:
            source = bundle.read(
                "Administration-main/src/components/tailadmin/EcommerceDashboard.tsx"
            ).decode()
        section = source.split("function MonthlyTarget", 1)[1].split(
            "function Statistics", 1
        )[0]
        texts = [
            re.sub(r"\s+", " ", text).strip()
            for text in re.findall(r">([^<>]+)<", section)
            if "{" not in text and text.strip()
        ]
        percentages = re.findall(r"(?:\+)?\d+(?:\.\d+)?%", " ".join(texts))
        if percentages:
            result["percentage"] = percentages[0]
            result["progress"] = min(
                100.0, max(0.0, float(percentages[0].strip("+%")))
            )
        if len(percentages) > 1:
            result["delta"] = percentages[1]
        result["description"] = next(
            (text for text in texts if "earned" in text.lower()), ""
        )
        for label, key in (
            ("Target", "target"),
            ("Revenue", "revenue"),
            ("Today", "today"),
        ):
            match = re.search(rf"{label}.*?(\$[\d,.]+[Kk]?)", section, re.S)
            if match:
                result[key] = match.group(1)
        if not result["percentage"]:
            value = re.search(r"value:\s*(\d+(?:\.\d+)?)", section)
            if value:
                result["progress"] = float(value.group(1))
                result["percentage"] = f"{result['progress']:.2f}%"
        return result
    except Exception as e:
        logging.exception(f"Error: {e}")
        return result


class DashboardState(rx.State):
    target_content: TargetContent = source_target()
    selected_range: str = "Monthly"

    @rx.event
    def select_range(self, value: str):
        self.selected_range = value
