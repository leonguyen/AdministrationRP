"""Runtime hosting resource metrics (CPU / memory / disk) via cgroups.

Ported from the Reflex app's HostingState. Pure functions; no framework deps.
"""
import asyncio
import logging
import shutil
import time
from pathlib import Path
from typing import TypedDict


class ResourceUsage(TypedDict):
    label: str
    icon: str
    used: float
    maximum: float
    percent: float
    quota: str
    badge: str
    color: str
    note: str


def _read_text(path: Path) -> str:
    try:
        return path.read_text().strip()
    except (OSError, UnicodeError) as e:
        logging.exception(f"Error: {e}")
        return ""


def _number(text: str) -> float:
    try:
        value = int(text)
        return float(value) if value >= 0 else -1.0
    except ValueError:
        return -1.0


def _cgroup_dir(root: Path = Path("/sys/fs/cgroup")) -> Path:
    membership = _read_text(Path("/proc/self/cgroup"))
    membership_path = next(
        (
            line[3:].lstrip("/")
            for line in membership.splitlines()
            if line.startswith("0::")
        ),
        "",
    )
    relative = Path(membership_path)
    candidate = root / relative
    if ".." not in relative.parts and (
        (candidate / "cpu.stat").is_file()
        or (candidate / "memory.current").is_file()
    ):
        return candidate
    return root


def _limits(directory: Path, root: Path) -> tuple[float, float]:
    cpu_limits: list[float] = []
    memory_limits: list[float] = []
    current = directory
    while current.is_relative_to(root):
        parts = _read_text(current / "cpu.max").split()
        if len(parts) == 2:
            quota = _number(parts[0])
            period = _number(parts[1])
            if quota > 0 and period > 0:
                cpu_limits.append(quota / period)
        memory = _number(_read_text(current / "memory.max"))
        if memory > 0:
            memory_limits.append(memory)
        if current == root:
            break
        current = current.parent
    return (
        min(cpu_limits) if cpu_limits else -1.0,
        min(memory_limits) if memory_limits else -1.0,
    )


def _cpu_usage(directory: Path) -> float:
    usage_value = next(
        (
            parts[1]
            for line in _read_text(directory / "cpu.stat").splitlines()
            if len(parts := line.split()) == 2 and parts[0] == "usage_usec"
        ),
        "",
    )
    return _number(usage_value)


def _row(
    label: str, icon: str, used: float, maximum: float, unit: str, note: str
) -> ResourceUsage:
    percent = used / maximum * 100 if used >= 0 and maximum > 0 else -1.0
    color = "gray"
    if percent >= 90:
        color = "red"
    elif percent >= 70:
        color = "orange"
    elif percent >= 0:
        color = "green"
    used_text = f"{used:.2f}" if used >= 0 else "N/A"
    maximum_text = f"{maximum:.2f}" if maximum > 0 else "N/A"
    return {
        "label": label,
        "icon": icon,
        "used": used,
        "maximum": maximum,
        "percent": percent,
        "quota": f"{used_text} / {maximum_text} {unit}",
        "badge": f"{percent:.1f}% used" if percent >= 0 else "N/A",
        "color": color,
        "note": note,
    }


def _cpu_row(before: float, after: float, elapsed: float, maximum: float) -> ResourceUsage:
    used = (
        (after - before) / 1_000_000 / elapsed
        if before >= 0 and after >= before and elapsed > 0
        else -1.0
    )
    note = "Average active vCPUs over a ~0.2 s sample; cgroup CPU quota."
    if used < 0:
        note = "CPU usage counter unavailable or reset; usage is N/A."
    elif maximum <= 0:
        note = "CPU usage measured; no finite cgroup CPU quota available."
    return _row("CPU", "cpu", used, maximum, "vCPUs", note)


def _remaining_rows(directory: Path, memory_limit: float) -> list[ResourceUsage]:
    memory = _number(_read_text(directory / "memory.current"))
    memory_note = "Cgroup memory usage / effective cgroup memory limit. GB uses decimal units."
    if memory < 0 or memory_limit <= 0:
        memory_note = "Cgroup memory usage or finite memory limit unavailable; N/A where unknown."
    rows = [
        _row(
            "Memory",
            "memory-stick",
            memory / 1e9 if memory >= 0 else -1.0,
            memory_limit / 1e9 if memory_limit > 0 else -1.0,
            "GB",
            memory_note,
        )
    ]
    try:
        disk = shutil.disk_usage("/")
        rows.append(
            _row(
                "Hard disk",
                "hard-drive",
                disk.used / 1e9,
                disk.total / 1e9,
                "GB",
                "Mounted filesystem used / total capacity. GB uses decimal units.",
            )
        )
    except OSError as e:
        logging.exception(f"Error: {e}")
        rows.append(
            _row(
                "Hard disk",
                "hard-drive",
                -1.0,
                -1.0,
                "GB",
                "Mounted filesystem measurement unavailable.",
            )
        )
    return rows


async def collect_metrics() -> list[ResourceUsage]:
    root = Path("/sys/fs/cgroup")
    directory = await asyncio.to_thread(_cgroup_dir, root)
    cpu_limit, memory_limit = await asyncio.to_thread(_limits, directory, root)
    before = await asyncio.to_thread(_cpu_usage, directory)
    started = time.monotonic()
    await asyncio.sleep(0.2)
    after = await asyncio.to_thread(_cpu_usage, directory)
    elapsed = time.monotonic() - started
    rows = [_cpu_row(before, after, elapsed, cpu_limit)]
    rows.extend(await asyncio.to_thread(_remaining_rows, directory, memory_limit))
    return rows


def initial_resources() -> list[ResourceUsage]:
    return [
        _row("CPU", "cpu", -1.0, -1.0, "vCPUs", "Not measured yet."),
        _row("Memory", "memory-stick", -1.0, -1.0, "GB", "Not measured yet."),
        _row("Hard disk", "hard-drive", -1.0, -1.0, "GB", "Not measured yet."),
    ]