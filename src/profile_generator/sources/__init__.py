"""Data sources.

A source fetches data and returns a JSON-serialisable dict. It is registered
here under a name, and its data appears in the template context under that
name (``{{ stats.hackathons }}``). Adding a source is one module plus one line
in ``SOURCES``.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from profile_generator.errors import SourceError
from profile_generator.http import JsonClient
from profile_generator.settings import Settings
from profile_generator.sources import stats, steam

__all__ = ["EMPTY", "SOURCES", "SourceError"]


Fetcher = Callable[[Settings, JsonClient], dict[str, Any]]

SOURCES: dict[str, Fetcher] = {
    "stats": stats.fetch,
    "steam": steam.fetch,
}

# What a source looks like when it has never succeeded (no snapshot yet).
EMPTY: dict[str, dict[str, Any]] = {
    "stats": stats.EMPTY,
    "steam": steam.EMPTY,
}
