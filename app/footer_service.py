"""Footer links fetched from a remote YAML API.

Ported from the Reflex app's FooterLinksState. Fetches a JSON envelope whose
`content` is YAML containing a `backlinks` list; validates http(s) URLs.
"""
import json
import logging
import urllib.request
from typing import TypedDict
from urllib.parse import urlsplit

import yaml


class FooterLink(TypedDict):
    label: str
    url: str


def _parse_document(response_body: bytes) -> list[FooterLink]:
    envelope = json.loads(response_body.decode("utf-8"))
    if not isinstance(envelope, dict) or not isinstance(
        envelope.get("content"), str
    ):
        raise ValueError("The document response did not contain YAML content.")
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


def fetch_links() -> list[FooterLink]:
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
    return _parse_document(response_body)