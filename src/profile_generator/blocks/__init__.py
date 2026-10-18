"""Blocks turn source data into ready-made Markdown/HTML snippets.

Each block is ``render(context) -> str`` and appears in the template as
``{{ blocks.<name> }}``. Blocks never fetch; they only format.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from profile_generator.blocks import badges, games

BLOCKS: dict[str, Callable[[dict[str, Any]], str]] = {
    "stat_badges": badges.stat_badges,
    "games": games.render,
}
