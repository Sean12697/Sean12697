"""Recently played Steam games with playtime and achievement progress.

Calls per run: one for the recent list, then per game one store lookup (to
hide adult-only titles) and one achievements lookup. Per-game lookups run in
parallel and fail soft: a game with no stats simply shows no achievement bar.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from typing import Any

from profile_generator.errors import SourceError
from profile_generator.http import HttpError, JsonClient

RECENT_URL = "https://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v1/"
STORE_URL = "https://store.steampowered.com/api/appdetails"
ACHIEVEMENTS_URL = "https://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v1/"

EMPTY: dict[str, Any] = {"games": []}


def fetch(settings, http: JsonClient) -> dict[str, Any]:
    if not settings.steam_api_key:
        raise SourceError("no Steam API key (set STEAM_API_KEY)")
    key, steam_id = settings.steam_api_key, settings.steam_id
    recent = http.get_json(
        RECENT_URL, {"key": key, "steamid": steam_id, "count": settings.steam_fetch}
    )
    games = (recent.get("response") or {}).get("games") or []

    def enrich(game: dict[str, Any]) -> dict[str, Any] | None:
        appid = game["appid"]
        if is_blocked(http, appid, settings.steam_blocked_descriptors):
            return None
        unlocked, total = achievements(http, key, steam_id, appid)
        return to_game(game, unlocked, total)

    with ThreadPoolExecutor(max_workers=5) as pool:
        enriched = [g for g in pool.map(enrich, games) if g]
    enriched.sort(key=lambda g: g["minutes_2weeks"], reverse=True)
    return {"games": enriched[: settings.steam_games]}


def to_game(game: dict[str, Any], unlocked: int | None, total: int | None) -> dict[str, Any]:
    two_weeks = int(game.get("playtime_2weeks", 0))
    forever = int(game.get("playtime_forever", 0))
    return {
        "appid": game["appid"],
        "name": game.get("name") or f"App {game['appid']}",
        "minutes_2weeks": two_weeks,
        "minutes_total": forever,
        "is_new": two_weeks > 0 and two_weeks >= forever,
        "achievements_unlocked": unlocked,
        "achievements_total": total,
    }


def is_blocked(http: JsonClient, appid: int, blocked: list[int]) -> bool:
    if not blocked:
        return False
    try:
        data = http.get_json(STORE_URL, {"appids": appid}).get(str(appid)) or {}
    except HttpError:
        return False  # store lookups are best effort
    if not data.get("success"):
        return False
    ids = ((data.get("data") or {}).get("content_descriptors") or {}).get("ids") or []
    return any(i in ids for i in blocked)


def achievements(
    http: JsonClient, key: str, steam_id: str, appid: int
) -> tuple[int | None, int | None]:
    """Return (unlocked, total), or (None, None) when the game has no achievements."""
    try:
        data = http.get_json(
            ACHIEVEMENTS_URL, {"key": key, "steamid": steam_id, "appid": appid, "l": "english"}
        )
    except HttpError:
        return None, None  # Steam answers 400 for games without stats
    rows = (data.get("playerstats") or {}).get("achievements") or []
    if not rows:
        return None, None
    return sum(1 for r in rows if r.get("achieved")), len(rows)
