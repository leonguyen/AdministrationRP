import reflex as rx
import reflex_xy

config = rx.Config(
    app_name="build_and_run_attached_zip",
    default_color_mode="light",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
        reflex_xy.XYPlugin(),
    ],
)
