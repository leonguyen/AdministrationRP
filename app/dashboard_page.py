"""Ecommerce dashboard page: metric cards + monthly-sales bar + monthly-target
gauge + statistics line chart (echarts).

Ported from the Reflex app's dashboard.py.
"""
from nicegui import ui

from .layout import page_title
from . import session

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
SALES_DATA = {
    "month": MONTHS,
    "value": [168, 385, 201, 298, 187, 195, 291, 110, 215, 390, 280, 112],
}
STATS_DATA = {
    "month": MONTHS,
    "sales": [180, 190, 170, 175, 160, 172, 170, 200, 225, 240, 235, 230],
    "revenue": [40, 30, 50, 45, 80, 95, 100, 120, 135, 150, 155, 140],
}

PRIMARY = "#465FFF"


def _metric(icon, label, value, delta, up):
    with ui.card().classes("w-full").style(
        "border-radius:1rem; border:1px solid var(--ta-border); background:#fff"
    ):
        with ui.element("div").classes(
            "flex items-center justify-center rounded-xl"
        ).style("width:3rem;height:3rem;background:var(--ta-soft)"):
            ui.icon(icon).classes("text-2xl").style("color: #374151")
        with ui.row().classes("items-end justify-between mt-5 w-full no-wrap"):
            with ui.column().classes("gap-0"):
                ui.label(label).classes("text-sm").style("color: var(--ta-muted)")
                ui.label(value).classes("text-3xl font-bold tracking-tight").style(
                    "color: var(--ta-text)"
                )
            color_cls = "green" if up else "red"
            arrow = "arrow_upward" if up else "arrow_downward"
            with ui.element("span").classes(f"ta-badge {color_cls} mb-1"):
                ui.icon(arrow).classes("text-xs")
                ui.label(delta)


def _monthly_sales():
    with ui.card().classes("w-full").style(
        "border-radius:1rem; border:1px solid var(--ta-border); background:#fff"
    ):
        ui.label("Monthly Sales").classes("ta-section-title mb-5")
        ui.echart({
            "grid": {"top": 10, "right": 0, "left": -20, "bottom": 0, "containLabel": True},
            "tooltip": {"trigger": "axis"},
            "xAxis": {
                "type": "category",
                "data": SALES_DATA["month"],
                "axisLine": {"lineStyle": {"color": "var(--ta-border)"}},
                "axisTick": {"show": False},
                "axisLabel": {"color": "var(--ta-muted)"},
            },
            "yAxis": {
                "type": "value",
                "axisLine": {"show": False},
                "axisTick": {"show": False},
                "splitLine": {"lineStyle": {"color": "var(--ta-border)", "type": "dashed"}},
                "axisLabel": {"color": "var(--ta-muted)"},
            },
            "series": [{
                "type": "bar",
                "name": "Sales",
                "data": SALES_DATA["value"],
                "itemStyle": {"color": PRIMARY, "borderRadius": [4, 4, 0, 0]},
                "barMaxWidth": 22,
            }],
        }).classes("w-full").style("height: 245px")


def _monthly_target():
    with ui.card().classes("w-full flex-1 overflow-hidden").style(
        "border-radius:1rem; border:1px solid var(--ta-border); background:var(--ta-soft)"
    ):
        with ui.card().classes("w-full").style(
            "border-radius:1rem; background:#fff"
        ):
            ui.label("Monthly Target").classes("ta-section-title")
            ui.label("Target you've set for each month").classes("text-sm mt-1").style(
                "color: var(--ta-muted)"
            )
            ui.echart({
                "series": [{
                    "type": "gauge",
                    "startAngle": 180,
                    "endAngle": 0,
                    "min": 0,
                    "max": 100,
                    "radius": "100%",
                    "progress": {"show": True, "width": 18, "roundCap": True,
                                 "itemStyle": {"color": PRIMARY}},
                    "axisLine": {"lineStyle": {"width": 18,
                                 "color": [[1, "#F3F4F6"]]}},
                    "pointer": {"show": False},
                    "axisTick": {"show": False},
                    "splitLine": {"show": False},
                    "axisLabel": {"show": False},
                    "detail": {
                        "valueAnimation": True,
                        "offsetCenter": [0, "0%"],
                        "fontSize": 36, "fontWeight": "bold",
                        "formatter": "{value}%",
                        "color": "var(--ta-text)",
                    },
                    "data": [{"value": 75.55}],
                }],
            }).classes("w-full mt-6").style("height: 210px")
            ui.linear_progress(value=0.7555, show_value=False).props(
                "color=#465FFF track-color=#F3F4F6 size=8px rounded"
            ).classes("mx-auto mb-5 w-52")
            ui.label("You earn $3287 today, it's higher than last month. Keep up your good work!").classes(
                "mx-auto max-w-xs text-center text-sm leading-6"
            ).style("color: var(--ta-muted)")
        with ui.row().classes("w-full no-wrap").style(
            "border-top:1px solid var(--ta-border); background:var(--ta-soft)"
        ):
            for lbl, up in [("Target", False), ("Revenue", True), ("Today", True)]:
                with ui.column().classes("flex-1 items-center py-6 gap-0"):
                    ui.label(lbl).classes("text-xs mb-2").style("color: var(--ta-muted)")
                    with ui.row().classes("items-center justify-center gap-1"):
                        ui.label("$20K").classes("text-base font-semibold").style(
                            "color: var(--ta-text)"
                        )
                        ui.icon("arrow_upward" if up else "arrow_downward").classes(
                            "text-base"
                        ).style("color: #16A34A" if up else "color: #DC2626")


def _range_toggle():
    ranges = ["Monthly", "Quarterly", "Annually"]
    state = {"selected": "Monthly"}
    with ui.element("div").classes("flex rounded-xl p-1").style(
        "background: var(--ta-bg)"
    ):
        btns = {}
        def make(label):
            b = ui.button(label).props("flat dense no-caps").classes(
                "px-3 py-2 text-sm font-medium"
            )
            def select():
                state["selected"] = label
                for name, btn in btns.items():
                    if name == label:
                        btn.classes("bg-white shadow-sm", remove="text-gray-500")
                        btn.style("color: var(--ta-text)")
                    else:
                        btn.classes(remove="bg-white shadow-sm")
                        btn.style("color: var(--ta-muted)")
            b.on_click(select)
            btns[label] = b
            return b
        for r in ranges:
            make(r)
    return state


def _statistics():
    with ui.card().classes("w-full").style(
        "border-radius:1rem; border:1px solid var(--ta-border); background:#fff"
    ):
        with ui.row().classes("items-start justify-between w-full mb-6 no-wrap"):
            with ui.column().classes("gap-1"):
                ui.label("Statistics").classes("ta-section-title")
                ui.label("Target you've set for each month").classes("text-sm").style(
                    "color: var(--ta-muted)"
                )
            with ui.row().classes("items-center gap-3 no-wrap"):
                _range_toggle()
                with ui.row().classes("items-center gap-2").style(
                    "border:1px solid var(--ta-border); border-radius:.5rem; padding:.625rem .75rem"
                ):
                    ui.icon("calendar_month").classes("text-base")
                    ui.label("Jun 29 to Jul 05").classes("text-sm").style(
                        "color: #4B5563"
                    )
        ui.echart({
            "grid": {"top": 10, "right": 10, "left": -20, "bottom": 0, "containLabel": True},
            "tooltip": {"trigger": "axis"},
            "legend": {"bottom": 0, "textStyle": {"color": "var(--ta-muted)"}},
            "xAxis": {
                "type": "category",
                "boundaryGap": False,
                "data": STATS_DATA["month"],
                "axisLine": {"lineStyle": {"color": "var(--ta-border)"}},
                "axisTick": {"show": False},
                "axisLabel": {"color": "var(--ta-muted)"},
            },
            "yAxis": {
                "type": "value",
                "axisLine": {"show": False},
                "axisTick": {"show": False},
                "splitLine": {"lineStyle": {"color": "var(--ta-border)", "type": "dashed"}},
                "axisLabel": {"color": "var(--ta-muted)"},
            },
            "series": [
                {
                    "name": "Sales", "type": "line", "smooth": True,
                    "data": STATS_DATA["sales"],
                    "lineStyle": {"color": PRIMARY, "width": 2.5},
                    "itemStyle": {"color": PRIMARY},
                    "areaStyle": {"color": PRIMARY, "opacity": 0.1},
                },
                {
                    "name": "Revenue", "type": "line", "smooth": True,
                    "data": STATS_DATA["revenue"],
                    "lineStyle": {"color": "#9CB9FF", "width": 2.5},
                    "itemStyle": {"color": "#9CB9FF"},
                    "areaStyle": {"color": "#9CB9FF", "opacity": 0.1},
                },
            ],
        }).classes("w-full").style("height: 290px")
        ui.label("Static source data · Range selection does not change the sample values.").classes(
            "mt-4 text-xs"
        ).style("color: var(--ta-muted)")


def _account_access_strip():
    with ui.element("section").classes("w-full").style(
        "background:#fff; border:1px solid var(--ta-border); border-radius:1rem; padding:1rem 1.25rem"
    ):
        authenticated = session.is_authenticated()
        name = session.display_name() if authenticated else "Your TailAdmin account"
        with ui.row().classes("items-center justify-between w-full no-wrap"):
            with ui.row().classes("items-center gap-3 min-w-0"):
                with ui.element("div").classes(
                    "flex items-center justify-center rounded-xl shrink-0"
                ).style(
                    "width:2.5rem;height:2.5rem;background:rgba(70,95,255,.10)"
                ):
                    ui.icon("person").classes("text-xl").style("color: var(--ta-primary)")
                with ui.column().classes("gap-1 min-w-0"):
                    ui.label(name).classes("text-sm font-semibold").style(
                        "color: var(--ta-text)"
                    )
                    ui.label(
                        "Sign in or create an account in this app."
                        if not authenticated else name
                    ).classes("text-sm").style("color: var(--ta-muted)")
            if authenticated:
                ui.link("View account", "/account").classes("ta-btn-primary").style(
                    "text-decoration:none"
                )
            else:
                with ui.row().classes("items-center gap-3 shrink-0 no-wrap"):
                    ui.button("Sign in", icon="login", on_click=lambda: ui.navigate.to("/auth")).classes(
                        "ta-btn"
                    )
                    ui.button("Sign up", icon="person_add", on_click=lambda: ui.navigate.to("/auth?mode=signup")).classes(
                        "ta-btn-primary"
                    )


def dashboard_content():
    with ui.column().classes("w-full gap-6"):
        page_title("Ecommerce", "")
        _account_access_strip()
        with ui.grid().classes("w-full gap-6 grid-cols-1 xl:grid-cols-3"):
            with ui.column().classes("gap-6 min-w-0 xl:col-span-2"):
                with ui.grid().classes("w-full gap-6 grid-cols-1 sm:grid-cols-2"):
                    _metric("group", "Customers", "3,782", "+11.01%", True)
                    _metric("inventory_2", "Orders", "5,359", "-9.05%", False)
                _monthly_sales()
            _monthly_target()
        _statistics()


def build():
    from .layout import shell

    shell("Ecommerce", dashboard_content)