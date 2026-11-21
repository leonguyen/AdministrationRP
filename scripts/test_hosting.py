import reflex as rx
import asyncio
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
from build_and_run_attached_zip.states.hosting_state import HostingState
from build_and_run_attached_zip.components.hosting_footer import hosting_footer, MantineProvider


class HostingMeasurements(unittest.TestCase):
    def test_thresholds_and_formatting(self):
        for percent, color in [
            (0, "green"),
            (69.9, "green"),
            (70, "orange"),
            (89.9, "orange"),
            (90, "red"),
            (110, "red"),
        ]:
            row = HostingState._row(
                "Memory", "memory-stick", percent, 100, "GB", ""
            )
            self.assertEqual(row["color"], color)
            self.assertEqual(row["badge"], f"{percent:.1f}% used")
            self.assertEqual(row["quota"], f"{percent:.2f} / 100.00 GB")

    def test_unavailable_limit_does_not_invent_quota(self):
        row = HostingState._row("CPU", "cpu", 0.5, -1, "vCPUs", "")
        self.assertEqual(row["badge"], "N/A")
        self.assertEqual(row["color"], "gray")
        self.assertEqual(row["quota"], "0.50 / N/A vCPUs")
        self.assertEqual(HostingState._number("max"), -1)

    def test_cpu_counter_sample(self):
        row = HostingState._cpu_row(1_000_000, 1_200_000, 0.2, 2)
        self.assertAlmostEqual(row["used"], 1)
        self.assertAlmostEqual(row["percent"], 50)
        self.assertEqual(
            HostingState._cpu_row(200, 100, 0.2, 2)["badge"], "N/A"
        )
        self.assertEqual(HostingState._cpu_row(-1, -1, 0.2, 2)["badge"], "N/A")

    def test_cgroup_ancestor_limits(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            child = root / "workload"
            child.mkdir()
            (root / "cpu.max").write_text("200000 100000")
            (root / "memory.max").write_text("2000000000")
            (child / "cpu.max").write_text("max 100000")
            (child / "memory.max").write_text("3000000000")
            (child / "cpu.stat").write_text(
                "usage_usec 12345\nuser_usec 9999\n"
            )
            self.assertEqual(
                HostingState._limits(child, root), (2, 2_000_000_000)
            )
            self.assertEqual(HostingState._cpu_usage(child), 12345)

    def test_memory_and_disk_from_real_interfaces(self):
        with TemporaryDirectory() as temporary:
            directory = Path(temporary)
            (directory / "memory.current").write_text("500000000")
            disk = shutil_result(
                total=5_000_000_000, used=1_000_000_000, free=4_000_000_000
            )
            with patch(
                "app.states.hosting_state.shutil.disk_usage", return_value=disk
            ) as disk_usage:
                rows = HostingState._remaining_rows(directory, 2_000_000_000)
            disk_usage.assert_called_once_with("/")
            self.assertEqual(rows[0]["percent"], 25)
            self.assertEqual(rows[1]["percent"], 20)
            self.assertEqual(rows[1]["quota"], "1.00 / 5.00 GB")

    def test_async_collection(self):
        with (
            patch.object(
                HostingState, "_cgroup_dir", return_value=Path("/test")
            ),
            patch.object(
                HostingState, "_limits", return_value=(2.0, 2_000_000_000.0)
            ),
            patch.object(
                HostingState,
                "_cpu_usage",
                side_effect=[1_000_000.0, 1_200_000.0],
            ),
            patch.object(HostingState, "_remaining_rows", return_value=[]),
        ):
            rows = asyncio.run(HostingState._collect_metrics())
        self.assertGreater(rows[0]["used"], 0)
        self.assertLessEqual(rows[0]["used"], 1)

    def test_footer_uses_real_mantine_and_bundled_css(self):
        self.assertIsInstance(hosting_footer(), rx.Component)
        provider = MantineProvider.create()
        imports = provider._get_imports()
        self.assertIn("@mantine/core/styles.css", imports)
        self.assertEqual(provider.tag, "MantineProvider")


from collections import namedtuple

shutil_result = namedtuple("DiskUsage", "total used free")


if __name__ == "__main__":
    unittest.main()
