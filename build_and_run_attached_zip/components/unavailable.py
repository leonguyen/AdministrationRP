import reflex as rx
from build_and_run_attached_zip.components.shell import page_title


def unavailable(
    title: str, icon: str, description: str, detail: str
) -> rx.Component:
    return rx.el.div(
        page_title(title, description),
        rx.el.section(
            rx.el.div(
                rx.el.div(
                    rx.icon(icon, class_name="h-8 w-8 text-[#465FFF]"),
                    class_name="mb-6 flex h-16 w-16 items-center justify-center rounded-2xl bg-indigo-50",
                ),
                rx.el.span(
                    rx.icon("circle-alert", class_name="h-3.5 w-3.5"),
                    "Feature unavailable",
                    class_name="mb-4 inline-flex w-fit items-center gap-2 rounded-full bg-amber-50 px-3 py-1.5 text-xs font-medium text-amber-800",
                ),
                rx.el.h2(
                    f"{title} is not enabled",
                    class_name="text-2xl font-semibold tracking-tight text-[#1D2939]",
                ),
                rx.el.p(
                    detail,
                    class_name="mt-4 max-w-2xl text-base leading-7 text-gray-500",
                ),
                rx.el.div(
                    rx.icon(
                        "shield-check",
                        class_name="mt-0.5 h-5 w-5 shrink-0 text-[#465FFF]",
                    ),
                    rx.el.div(
                        rx.el.p(
                            "No GitHub repository activity is performed",
                            class_name="text-sm font-semibold text-[#1D2939]",
                        ),
                        rx.el.p(
                            "Reflex account sign-up and sign-in are available separately. GitHub connections, repository saving, commits, merges, and GitHub requests are not simulated or executed.",
                            class_name="mt-2 text-sm leading-6 text-gray-500",
                        ),
                    ),
                    class_name="mt-7 flex gap-3 rounded-xl border border-gray-200 bg-[#F9FAFB] p-5",
                ),
                rx.el.div(
                    rx.el.a(
                        rx.icon("arrow-left", class_name="h-4 w-4"),
                        "Back to dashboard",
                        href="/",
                        class_name="inline-flex items-center justify-center gap-2 rounded-lg bg-[#465FFF] px-4 py-3 text-sm font-medium text-white hover:bg-[#3641D9] focus-visible:ring-2 focus-visible:ring-[#465FFF] focus-visible:ring-offset-2",
                    ),
                    rx.el.a(
                        "Manage menu",
                        rx.icon("arrow-right", class_name="h-4 w-4"),
                        href="/menu",
                        class_name="inline-flex items-center justify-center gap-2 rounded-lg border border-gray-200 px-4 py-3 text-sm font-medium text-gray-700 hover:bg-gray-50 focus-visible:ring-2 focus-visible:ring-[#465FFF]",
                    ),
                    class_name="mt-8 flex flex-wrap gap-3",
                ),
                class_name="w-full max-w-3xl",
            ),
            class_name="flex min-h-[480px] w-full items-center rounded-2xl border border-gray-200 bg-white p-6 sm:p-10 lg:p-12",
        ),
        class_name="w-full",
    )
