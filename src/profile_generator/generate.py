"""Pipeline: sources -> context -> blocks -> template -> README."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from importlib import resources
from typing import Any

from profile_generator.blocks import BLOCKS
from profile_generator.errors import SourceError
from profile_generator.http import HttpError, JsonClient, UrllibClient
from profile_generator.settings import Settings
from profile_generator.sources import EMPTY, SOURCES
from profile_generator.template import render as render_template

log = logging.getLogger("profile_generator")


@dataclass
class Result:
    context: dict[str, Any]
    markdown: str
    failures: dict[str, str] = field(default_factory=dict)


def demo_data() -> dict[str, Any]:
    raw = resources.files("profile_generator").joinpath("demo/context.json").read_text("utf-8")
    return json.loads(raw)


def collect(settings: Settings, http: JsonClient | None = None) -> tuple[dict, dict[str, str]]:
    """Fetch every source; a failing source falls back to its EMPTY defaults."""
    if settings.offline:
        return demo_data(), {}
    http = http or UrllibClient(timeout=settings.timeout, retries=settings.retries)
    data: dict[str, Any] = {}
    failures: dict[str, str] = {}
    for name, fetch in SOURCES.items():
        try:
            data[name] = fetch(settings, http)
            log.info("source %s: ok", name)
        except (SourceError, HttpError, KeyError, TypeError, ValueError) as exc:
            failures[name] = str(exc)
            log.warning("source %s failed (%s); using fallback text", name, exc)
            data[name] = EMPTY[name]
    return data, failures


def build_context(data: dict[str, Any], now: datetime | None = None) -> dict[str, Any]:
    now = now or datetime.now(UTC)
    ctx: dict[str, Any] = {
        **data,
        "generated_at": f"{now.day} {now:%B %Y, %H:%M} UTC",
        "generated_date": now.strftime("%Y-%m-%d"),
    }
    ctx["blocks"] = {name: block(ctx) for name, block in BLOCKS.items()}
    return ctx


def generate(
    settings: Settings,
    http: JsonClient | None = None,
    now: datetime | None = None,
) -> Result:
    data, failures = collect(settings, http)
    ctx = build_context(data, now)
    template = settings.template.read_text(encoding="utf-8")
    markdown = render_template(template, ctx).rstrip() + "\n"
    return Result(context=ctx, markdown=markdown, failures=failures)
