import reflex as rx
from build_and_run_attached_zip.states.footer_links_state import FooterLinksState


def footer_links() -> rx.Component:
    return rx.cond(
        FooterLinksState.links.length() > 0,
        rx.el.footer(
            rx.foreach(
                FooterLinksState.links,
                lambda item: rx.el.a(
                    item["label"],
                    href=item["url"],
                    target="_blank",
                    rel="noopener noreferrer",
                    key=item["url"],
                    class_name="rounded-sm text-xs font-medium text-[#465FFF] hover:underline focus-visible:outline-hidden focus-visible:ring-2 focus-visible:ring-[#465FFF]",
                ),
            ),
            aria_busy=FooterLinksState.loading,
            class_name="mt-4 flex w-full shrink-0 flex-wrap items-center justify-center text-center gap-x-5 gap-y-2 pt-4",
        ),
    )
