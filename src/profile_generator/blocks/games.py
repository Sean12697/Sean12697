"""Recently played games as a compact HTML table (GitHub-safe)."""

from __future__ import annotations

import html
from typing import Any

HEADER_IMG = "https://cdn.cloudflare.steamstatic.com/steam/apps/{appid}/header.jpg"
STORE_URL = "https://store.steampowered.com/app/{appid}"
EMPTY_MESSAGE = (
    "<p><i>Nothing on Steam in the last couple of weeks. Probably at a beer festival.</i></p>"
)


def hours(minutes: int) -> str:
    if minutes < 60:
        return f"{minutes} min"
    h = minutes / 60
    return f"{h:,.0f} h" if h >= 100 else f"{h:,.1f} h"


def bar(unlocked: int, total: int, width: int = 10) -> str:
    filled = round(width * unlocked / total) if total else 0
    if unlocked and not filled:
        filled = 1
    return "▰" * filled + "▱" * (width - filled)


def row(game: dict[str, Any]) -> str:
    appid = game["appid"]
    name = html.escape(game["name"])
    store = STORE_URL.format(appid=appid)
    new = " &nbsp;<sup>🆕 new</sup>" if game.get("is_new") else ""
    lines = [
        f"<b><a href=\"{store}\">{name}</a></b>{new}",
        f"🕒 {hours(game['minutes_2weeks'])} in the last 2 weeks"
        f" · {hours(game['minutes_total'])} total",
    ]
    unlocked, total = game.get("achievements_unlocked"), game.get("achievements_total")
    if total:
        pct = round(100 * unlocked / total)
        progress = f"<code>{bar(unlocked, total)}</code> {unlocked}/{total}"
        lines.append(f"🏆 {progress} achievements ({pct}%)")
    img = HEADER_IMG.format(appid=appid)
    return (
        "<tr>"
        f'<td width="190"><a href="{store}"><img src="{img}" width="184" alt="{name}"></a></td>'
        f"<td>{'<br>'.join(lines)}</td>"
        "</tr>"
    )


def render(ctx: dict[str, Any]) -> str:
    games = ctx["steam"]["games"]
    if not games:
        return EMPTY_MESSAGE
    return "<table>\n" + "\n".join(row(g) for g in games) + "\n</table>"
