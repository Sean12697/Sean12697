"""Tiny JSON-over-HTTP client on the standard library, with retries."""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Protocol

from profile_generator import __version__

USER_AGENT = f"profile-generator/{__version__} (+https://github.com/Sean12697/Sean12697)"


class HttpError(Exception):
    def __init__(self, url: str, status: int | None, message: str):
        super().__init__(f"{status or 'network'} error for {url}: {message}")
        self.url = url
        self.status = status


class JsonClient(Protocol):
    def get_json(self, url: str, params: dict[str, Any] | None = None) -> Any: ...


class UrllibClient:
    def __init__(self, timeout: float = 20.0, retries: int = 2, backoff: float = 1.5):
        self.timeout = timeout
        self.retries = retries
        self.backoff = backoff

    def get_json(self, url: str, params: dict[str, Any] | None = None) -> Any:
        full = f"{url}?{urllib.parse.urlencode(params)}" if params else url
        safe = url  # never log query strings: they can carry API keys
        request = urllib.request.Request(
            full, headers={"User-Agent": USER_AGENT, "Accept": "application/json"}
        )
        for attempt in range(self.retries + 1):
            try:
                with urllib.request.urlopen(request, timeout=self.timeout) as resp:
                    return json.loads(resp.read().decode("utf-8"))
            except urllib.error.HTTPError as exc:
                transient = exc.code == 429 or exc.code >= 500
                if not transient or attempt == self.retries:
                    raise HttpError(safe, exc.code, exc.reason) from None
            except (urllib.error.URLError, TimeoutError) as exc:
                if attempt == self.retries:
                    raise HttpError(safe, None, str(exc)) from None
            except json.JSONDecodeError as exc:
                raise HttpError(safe, None, f"invalid JSON ({exc})") from None
            time.sleep(self.backoff * (attempt + 1))
        raise AssertionError("unreachable")
