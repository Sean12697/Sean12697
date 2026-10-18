"""shields.io badges for the headline numbers."""

from __future__ import annotations

import html
import urllib.parse
from typing import Any


def shield(label: str, message: str, color: str, logo: str | None = None) -> str:
    def part(text: str) -> str:
        text = str(text).replace("-", "--").replace("_", "__")
        return urllib.parse.quote(text, safe="")

    url = f"https://img.shields.io/badge/{part(label)}-{part(message)}-{color}?style=for-the-badge"
    if logo:
        url += f"&logo={urllib.parse.quote(logo)}&logoColor=white"
    return url


def badge(label: str, message: str, color: str, href: str, logo: str | None = None) -> str:
    alt = html.escape(f"{label}: {message}")
    src = html.escape(shield(label, message, color, logo))
    return f'<a href="{html.escape(href)}"><img alt="{alt}" src="{src}"></a>'


def stat_badges(ctx: dict[str, Any]) -> str:
    stats = ctx["stats"]
    return "\n".join(
        [
            badge(
                "Hackathons",
                stats["hackathons"],
                "7C3AED",
                "https://seanomahoney.com/timeline/collection/hackathons",
                "devpost",
            ),
            badge(
                "Beer festivals",
                stats["beer_festivals"],
                "D97706",
                "https://seanomahoney.com/timeline/collection/beer-festivals",
            ),
            badge(
                "Unique beers",
                stats["beers"],
                "FFC000",
                "https://untappd.com/user/sean12697",
                "untappd",
            ),
        ]
    )
