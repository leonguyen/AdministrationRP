import reflex as rx
from reflex.utils.imports import ImportVar
from build_and_run_attached_zip.states.hosting_state import HostingState, ResourceUsage


class MantineProvider(rx.Component):
    library = "@mantine/core@7.17.8"
    lib_dependencies = ["@mantine/hooks@7.17.8"]
    tag = "MantineProvider"
    theme: rx.Var[dict[str, str]]
    force_color_scheme: rx.Var[str]

    def _get_imports(self) -> dict[str, list[ImportVar]]:
        return {
            **super()._get_imports(),
            "@mantine/core/styles.css": [ImportVar(tag=None)],
        }


class MantineAccordion(rx.Component):
    library = "@mantine/core@7.17.8"
    tag = "Accordion"
    order: rx.Var[int]
    keep_mounted: rx.Var[bool]


class MantineAccordionItem(rx.Component):
    library = "@mantine/core@7.17.8"
    tag = "Accordion.Item"
    value: rx.Var[str]


class MantineAccordionControl(rx.Component):
    library = "@mantine/core@7.17.8"
    tag = "Accordion.Control"


class MantineAccordionPanel(rx.Component):
    library = "@mantine/core@7.17.8"
    tag = "Accordion.Panel"


class MantineBadge(rx.Component):
    library = "@mantine/core@7.17.8"
    tag = "Badge"
    color: rx.Var[str]
    variant: rx.Var[str]


def resource_row(resource: ResourceUsage) -> rx.Component:
    return rx.el.div(
        rx.el.div(
            rx.icon(
                resource["icon"], class_name="h-4 w-4 shrink-0 text-gray-500"
            ),
            rx.el.span(
                resource["label"],
                class_name="text-sm font-medium text-[#1D2939]",
            ),
            class_name="flex items-center gap-2",
        ),
        rx.el.div(
            MantineBadge.create(
                resource["badge"],
                color=resource["color"],
                variant="light",
                class_name="w-fit normal-case",
            ),
            rx.el.span(
                resource["quota"],
                class_name="text-sm font-medium tabular-nums text-[#1D2939]",
            ),
            class_name="flex flex-wrap items-center gap-3 sm:justify-end",
        ),
        rx.el.p(
            resource["note"],
            class_name="text-xs leading-5 text-gray-600 sm:col-span-2",
        ),
        key=resource["label"],
        class_name="grid grid-cols-1 gap-2 border-b border-gray-200 py-3 last:border-b-0 sm:grid-cols-2",
    )


def hosting_footer() -> rx.Component:
    return rx.el.footer(
        MantineProvider.create(
            MantineAccordion.create(
                MantineAccordionItem.create(
                    MantineAccordionControl.create(
                        rx.el.span(
                            rx.icon(
                                "server", class_name="h-4 w-4 text-[#465FFF]"
                            ),
                            rx.el.span(
                                "Hosting resources",
                                class_name="text-sm font-semibold text-[#1D2939]",
                            ),
                            class_name="flex items-center gap-2",
                        ),
                        aria_label="Hosting resources",
                        class_name="bg-white hover:bg-gray-50 focus-visible:ring-2 focus-visible:ring-[#465FFF]",
                    ),
                    MantineAccordionPanel.create(
                        rx.el.div(
                            rx.foreach(HostingState.resources, resource_row),
                            aria_busy=HostingState.refreshing,
                            class_name="w-full bg-white text-[#1D2939]",
                        ),
                        rx.el.p(
                            "Runtime container usage; disk is mounted filesystem capacity, not account plan quota.",
                            class_name="mt-3 text-xs leading-5 text-gray-600",
                        ),
                        rx.el.div(
                            rx.el.p(
                                "Last updated: ",
                                rx.cond(
                                    HostingState.updated_iso != "",
                                    rx.el.time(
                                        HostingState.last_updated,
                                        date_time=HostingState.updated_iso,
                                    ),
                                    rx.el.span(HostingState.last_updated),
                                ),
                                aria_live="polite",
                                class_name="text-xs text-gray-600",
                            ),
                            rx.el.button(
                                rx.icon(
                                    "refresh-cw",
                                    class_name=rx.cond(
                                        HostingState.refreshing,
                                        "h-3.5 w-3.5 animate-spin",
                                        "h-3.5 w-3.5",
                                    ),
                                ),
                                rx.cond(
                                    HostingState.refreshing,
                                    "Refreshing…",
                                    "Refresh",
                                ),
                                type="button",
                                on_click=HostingState.refresh_metrics,
                                disabled=HostingState.refreshing,
                                aria_label="Refresh hosting resource measurements",
                                class_name="inline-flex items-center gap-2 rounded-lg border border-gray-200 bg-white px-3 py-2 text-xs font-medium text-[#465FFF] hover:bg-indigo-50 focus-visible:ring-2 focus-visible:ring-[#465FFF] disabled:cursor-wait disabled:opacity-60",
                            ),
                            class_name="mt-4 flex flex-wrap items-center justify-between gap-3 border-t border-gray-200 pt-3",
                        ),
                        rx.cond(
                            HostingState.error != "",
                            rx.el.p(
                                HostingState.error,
                                role="alert",
                                class_name="mt-3 rounded-lg bg-red-100 p-3 text-xs text-red-800",
                            ),
                        ),
                    ),
                    value="resources",
                    class_name="border-0 bg-white",
                ),
                order=2,
                keep_mounted=True,
                class_name="w-full bg-white text-[#1D2939]",
            ),
            theme={"fontFamily": "Inter, sans-serif"},
            force_color_scheme="light",
        ),
        aria_label="Runtime hosting resource usage",
        class_name="mt-6 w-full shrink-0 overflow-hidden rounded-2xl border border-gray-200 bg-white text-[#1D2939]",
    )
