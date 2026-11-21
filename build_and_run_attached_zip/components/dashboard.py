import reflex as rx
import reflex_xy as rxy
import xy
from build_and_run_attached_zip.components.shell import page_title
from build_and_run_attached_zip.components.account_access import account_access_strip
from build_and_run_attached_zip.states.dashboard_state import DashboardState


MONTHS = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]
SALES_DATA = {
    "month": MONTHS,
    "value": [168, 385, 201, 298, 187, 195, 291, 110, 215, 390, 280, 112],
}
STATS_DATA = {
    "month": MONTHS,
    "sales": [180, 190, 170, 175, 160, 172, 170, 200, 225, 240, 235, 230],
    "revenue": [40, 30, 50, 45, 80, 95, 100, 120, 135, 150, 155, 140],
}


def metric(
    icon: str, label: str, value: str, delta: str, up: bool
) -> rx.Component:
    return rx.el.article(
        rx.el.div(
            rx.icon(icon, class_name="h-6 w-6 text-gray-700"),
            class_name="flex h-12 w-12 items-center justify-center rounded-xl bg-gray-100",
        ),
        rx.el.div(
            rx.el.div(
                rx.el.h2(
                    label,
                    class_name="text-sm font-normal text-gray-500",
                ),
                rx.el.p(
                    value,
                    class_name="mt-2 text-3xl font-bold tracking-tight text-[#1D2939]",
                ),
            ),
            rx.el.span(
                rx.cond(
                    up,
                    rx.icon("arrow-up-right", class_name="h-3.5 w-3.5"),
                    rx.icon("arrow-down-right", class_name="h-3.5 w-3.5"),
                ),
                delta,
                class_name=rx.cond(
                    up,
                    "mb-1 inline-flex w-fit items-center gap-1 rounded-full bg-green-100 px-2 py-1 text-xs font-medium text-green-800",
                    "mb-1 inline-flex w-fit items-center gap-1 rounded-full bg-red-100 px-2 py-1 text-xs font-medium text-red-700",
                ),
            ),
            class_name="mt-5 flex items-end justify-between gap-2",
        ),
        class_name="w-full rounded-2xl border border-gray-200 bg-white p-6",
    )


def monthly_sales() -> rx.Component:
    return rx.el.section(
        rx.el.h2(
            "Monthly Sales",
            class_name="mb-5 text-lg font-semibold text-[#1D2939]",
        ),
        rx.el.div(
            rxy.chart(
                xy.bar(
                    "month",
                    "value",
                    color="#465FFF",
                    corner_radius=4,
                    width=0.45,
                    name="Sales",
                ),
                xy.x_axis(),
                xy.y_axis(),
                xy.modebar(False),
                xy.interaction_config(navigation=False),
                data=SALES_DATA,
                height="245px",
                class_name="min-w-[300px] w-full",
            ),
            class_name="h-[245px] w-full shrink-0 overflow-x-auto rounded-lg bg-white",
        ),
        class_name="w-full rounded-2xl border border-gray-200 bg-white p-6",
    )


def target_stat(label: str, key: str, up: bool) -> rx.Component:
    return rx.el.div(
        rx.el.p(label, class_name="mb-2 text-xs text-gray-500"),
        rx.el.p(
            rx.cond(
                DashboardState.target_content[key] != "",
                DashboardState.target_content[key],
                "—",
            ),
            rx.cond(
                up,
                rx.icon("arrow-up", class_name="h-4 w-4 text-green-600"),
                rx.icon("arrow-down", class_name="h-4 w-4 text-red-600"),
            ),
            class_name="flex items-center justify-center gap-1 text-base font-semibold text-[#1D2939]",
        ),
        class_name="flex-1 text-center",
    )


def monthly_target() -> rx.Component:
    return rx.el.section(
        rx.el.div(
            rx.el.h2(
                "Monthly Target",
                class_name="text-lg font-semibold text-[#1D2939]",
            ),
            rx.el.p(
                "Target you’ve set for each month",
                class_name="mt-1 text-sm text-gray-500",
            ),
            rx.el.div(
                rx.el.div(
                    class_name="absolute inset-x-0 top-2 mx-auto h-36 w-64 rounded-t-full border-[18px] border-b-0 border-gray-100"
                ),
                rx.el.div(
                    class_name="absolute inset-x-0 top-2 mx-auto h-36 w-64 rounded-t-full border-[18px] border-b-0 border-[#465FFF]/20"
                ),
                rx.el.div(
                    rx.el.p(
                        rx.cond(
                            DashboardState.target_content["percentage"] != "",
                            DashboardState.target_content["percentage"],
                            "—",
                        ),
                        class_name="text-4xl font-semibold tracking-tight text-[#1D2939]",
                    ),
                    rx.cond(
                        DashboardState.target_content["delta"] != "",
                        rx.el.span(
                            DashboardState.target_content["delta"],
                            class_name="mx-auto mt-3 block w-fit rounded-full bg-green-100 px-2 py-1 text-xs font-medium text-green-800",
                        ),
                    ),
                    class_name="relative z-10 pt-20 text-center",
                ),
                role="img",
                aria_label=f"Monthly target: {DashboardState.target_content['percentage']}",
                class_name="relative mx-auto mb-4 mt-6 h-44 w-full",
            ),
            rx.el.progress(
                value=DashboardState.target_content["progress"],
                max=100,
                aria_label="Monthly target completion",
                class_name="mx-auto mb-5 block h-2 w-52 overflow-hidden rounded-full border-0 bg-gray-100 text-[#465FFF] [&::-webkit-progress-bar]:bg-gray-100 [&::-webkit-progress-value]:rounded-full [&::-webkit-progress-value]:bg-[#465FFF] [&::-moz-progress-bar]:bg-[#465FFF]",
            ),
            rx.cond(
                DashboardState.target_content["description"] != "",
                rx.el.p(
                    DashboardState.target_content["description"],
                    class_name="mx-auto max-w-xs text-center text-sm leading-6 text-gray-500",
                ),
                rx.el.p(
                    "Original static monthly target sample.",
                    class_name="text-center text-sm text-gray-500",
                ),
            ),
            class_name="min-h-0 flex-1 rounded-2xl bg-white p-6",
        ),
        rx.el.div(
            target_stat("Target", "target", False),
            target_stat("Revenue", "revenue", True),
            target_stat("Today", "today", True),
            class_name="flex shrink-0 divide-x divide-gray-200 border-t border-gray-200 bg-gray-50 px-4 py-6",
        ),
        class_name="flex w-full flex-col overflow-hidden rounded-2xl border border-gray-200 bg-gray-50",
    )


def range_button(label: str) -> rx.Component:
    return rx.el.button(
        label,
        type="button",
        on_click=DashboardState.select_range(label),
        aria_pressed=DashboardState.selected_range == label,
        class_name=rx.cond(
            DashboardState.selected_range == label,
            "relative z-10 min-w-0 rounded-lg bg-transparent px-3 py-2 text-sm font-medium text-[#1D2939] focus-visible:outline-hidden focus-visible:ring-2 focus-visible:ring-[#465FFF] focus-visible:ring-offset-2",
            "relative z-10 min-w-0 rounded-lg bg-transparent px-3 py-2 text-sm font-medium text-gray-500 hover:text-[#1D2939] focus-visible:outline-hidden focus-visible:ring-2 focus-visible:ring-[#465FFF] focus-visible:ring-offset-2",
        ),
    )


def statistics() -> rx.Component:
    return rx.el.section(
        rx.el.div(
            rx.el.div(
                rx.el.h2(
                    "Statistics",
                    class_name="text-lg font-semibold text-[#1D2939]",
                ),
                rx.el.p(
                    "Target you’ve set for each month",
                    class_name="mt-1 text-sm text-gray-500",
                ),
            ),
            rx.el.div(
                rx.el.div(
                    rx.el.div(
                        rx.el.div(
                            aria_hidden=True,
                            class_name=rx.match(
                                DashboardState.selected_range,
                                (
                                    "Quarterly",
                                    "pointer-events-none absolute inset-y-0 left-0 w-1/3 translate-x-full rounded-lg border border-gray-200 bg-white shadow-xs transition-transform duration-200 ease-[cubic-bezier(0.23,1,0.32,1)] motion-reduce:transition-none",
                                ),
                                (
                                    "Annually",
                                    "pointer-events-none absolute inset-y-0 left-0 w-1/3 translate-x-[200%] rounded-lg border border-gray-200 bg-white shadow-xs transition-transform duration-200 ease-[cubic-bezier(0.23,1,0.32,1)] motion-reduce:transition-none",
                                ),
                                "pointer-events-none absolute inset-y-0 left-0 w-1/3 translate-x-0 rounded-lg border border-gray-200 bg-white shadow-xs transition-transform duration-200 ease-[cubic-bezier(0.23,1,0.32,1)] motion-reduce:transition-none",
                            ),
                        ),
                        rx.foreach(
                            ["Monthly", "Quarterly", "Annually"], range_button
                        ),
                        class_name="relative isolate grid grid-cols-3",
                    ),
                    role="group",
                    aria_label="Statistics range",
                    class_name="w-full rounded-xl bg-[#F9FAFB] p-1 sm:w-auto",
                ),
                rx.el.span(
                    rx.icon("calendar-days", class_name="h-4 w-4"),
                    "Jun 29 to Jul 05",
                    class_name="inline-flex items-center gap-2 rounded-lg border border-gray-200 px-3 py-2.5 text-sm text-gray-600",
                ),
                class_name="flex flex-wrap items-center gap-3",
            ),
            class_name="mb-6 flex flex-wrap items-center justify-between gap-4",
        ),
        rx.el.div(
            rxy.chart(
                xy.line(
                    "month",
                    "sales",
                    name="Sales",
                    color="#465FFF",
                    width=2.5,
                    curve="smooth",
                ),
                xy.line(
                    "month",
                    "revenue",
                    name="Revenue",
                    color="#9CB9FF",
                    width=2.5,
                    curve="smooth",
                ),
                xy.x_axis(),
                xy.y_axis(),
                xy.legend(),
                xy.modebar(False),
                xy.interaction_config(navigation=False),
                data=STATS_DATA,
                height="290px",
                class_name="min-w-[300px] w-full",
            ),
            class_name="h-[290px] w-full shrink-0 overflow-x-auto rounded-lg bg-white",
        ),
        rx.el.p(
            "Static source data · Range selection does not change the sample values.",
            class_name="mt-4 text-xs text-gray-500",
        ),
        class_name="w-full rounded-2xl border border-gray-200 bg-white p-6",
    )


def dashboard() -> rx.Component:
    return rx.el.div(
        page_title("Ecommerce", ""),
        account_access_strip(),
        rx.el.div(
            rx.el.div(
                rx.el.div(
                    metric("users", "Customers", "3,782", "+11.01%", True),
                    metric("package", "Orders", "5,359", "-9.05%", False),
                    class_name="grid grid-cols-1 gap-6 sm:grid-cols-2",
                ),
                monthly_sales(),
                class_name="flex min-w-0 flex-col gap-6 xl:col-span-2",
            ),
            monthly_target(),
            class_name="grid w-full grid-cols-1 items-stretch gap-6 xl:grid-cols-3",
        ),
        statistics(),
        class_name="flex w-full min-w-0 flex-col gap-6",
    )
