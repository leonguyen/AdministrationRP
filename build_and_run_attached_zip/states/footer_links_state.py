import asyncio
import json
import logging
import time
import urllib.request
import yaml
from typing import TypedDict
from urllib.parse import urlsplit

import reflex as rx


class FooterLink(TypedDict):
    label: str
    url: str


class FooterLinksState(rx.State):
    links: list[FooterLink] = []
    loading: bool = False
    error: str = ""
    _last_loaded_at: float = 0.0

    @staticmethod
    def _parse_document(response_body: bytes) -> list[FooterLink]:
        envelope = json.loads(response_body.decode("utf-8"))
        if not isinstance(envelope, dict) or not isinstance(
            envelope.get("content"), str
        ):
            raise ValueError(
                "The document response did not contain YAML content."
            )
        document = yaml.safe_load(envelope["content"])
        if not isinstance(document, dict):
            raise ValueError("The document YAML must contain a mapping.")
        backlinks = document.get("backlinks")
        if not isinstance(backlinks, list):
            raise ValueError("The document YAML must contain a backlinks list.")

        valid_links: list[FooterLink] = []
        for item in backlinks:
            if not isinstance(item, dict):
                continue
            label = item.get("label")
            url = item.get("url")
            if not isinstance(label, str) or not isinstance(url, str):
                continue
            label = label.strip()
            url = url.strip()
            if not label or not url:
                continue
            try:
                parsed_url = urlsplit(url)
                valid_host = bool(parsed_url.hostname and parsed_url.netloc)
                valid_scheme = parsed_url.scheme.lower() in {"http", "https"}
                has_no_credentials = (
                    parsed_url.username is None and parsed_url.password is None
                )
                parsed_url.port
            except ValueError:
                continue
            if valid_host and valid_scheme and has_no_credentials:
                valid_links.append({"label": label, "url": url})
        return valid_links

    @staticmethod
    def _fetch_links() -> list[FooterLink]:
        request = urllib.request.Request(
            "https://phabyycvxbizmxoyfxwa.supabase.co/functions/v1/yaml-api/documents/71406c55-ed1f-4fb5-a021-aa7c7ce902de",
            headers={
                "Accept": "application/json",
                "User-Agent": "TailAdmin/1.0",
            },
        )
        with urllib.request.urlopen(request, timeout=12) as response:
            response_body = response.read(1_000_001)
        if len(response_body) > 1_000_000:
            raise ValueError("The document response exceeded the allowed size.")
        return FooterLinksState._parse_document(response_body)

    @rx.event(background=True)
    async def load(self):
        async with self:
            if self.loading or (
                self._last_loaded_at > 0
                and time.monotonic() - self._last_loaded_at < 60
            ):
                return
            self.loading = True
            self.error = ""
        try:
            links = await asyncio.to_thread(FooterLinksState._fetch_links)
            async with self:
                self.links = links
                self._last_loaded_at = time.monotonic()
        except Exception as e:
            logging.exception(f"Error: {e}")
            async with self:
                self.error = "Unable to refresh footer links."
        finally:
            async with self:
                self.loading = False
