"""Portfolio stats from seanomahoney.com/stats.json.

Exposes the three headline numbers by name, plus the whole document as
``raw`` so the template can reach anything else (``{{ stats.raw.content.blogPosts }}``).
"""

from __future__ import annotations

from typing import Any

from profile_generator.errors import SourceError
from profile_generator.http import JsonClient

EMPTY: dict[str, Any] = {
    "hackathons": "many",
    "beer_festivals": "many",
    "beers": "thousands of",
    "generated_at": "",
    "raw": {},
}


def parse(doc: dict[str, Any]) -> dict[str, Any]:
    timeline = doc.get("timeline") or {}
    untappd = doc.get("untappd") or {}
    missing = [
        name
        for name, value in (
            ("timeline.hackathons", timeline.get("hackathons")),
            ("timeline.beerFestivals", timeline.get("beerFestivals")),
            ("untappd.formattedBeers", untappd.get("formattedBeers")),
        )
        if value in (None, "")
    ]
    if missing:
        raise SourceError(f"stats.json is missing {', '.join(missing)}")
    return {
        "hackathons": timeline["hackathons"],
        "beer_festivals": timeline["beerFestivals"],
        "beers": untappd["formattedBeers"],
        "generated_at": doc.get("generatedAt", ""),
        "raw": doc,
    }


def fetch(settings, http: JsonClient) -> dict[str, Any]:
    return parse(http.get_json(settings.stats_url))
