from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from profile_generator.http import HttpError
from profile_generator.settings import Settings

FIXTURES = Path(__file__).parent / "fixtures"
ROOT = Path(__file__).parent.parent


def fixture(name: str) -> Any:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


class FakeHttp:
    """Routes get_json calls to canned responses: {url: response | callable | Exception}."""

    def __init__(self, routes: dict[str, Any]):
        self.routes = routes
        self.calls: list[tuple[str, dict]] = []

    def get_json(self, url: str, params: dict | None = None) -> Any:
        self.calls.append((url, params or {}))
        if url not in self.routes:
            raise HttpError(url, 404, "no route")
        route = self.routes[url]
        if callable(route):
            route = route(params or {})
        if isinstance(route, Exception):
            raise route
        return route


def settings(tmp: Path, **kw: Any) -> Settings:
    base = {
        "template": ROOT / "template.md",
        "output": tmp / "README.md",
        "steam_api_key": "test-key",
    }
    base.update(kw)
    return Settings.load(config=None, env_file=None, environ={}, overrides=base)
