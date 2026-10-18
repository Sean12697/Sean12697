"""A deliberately small template engine.

``{{ dotted.path }}`` is replaced with the value at that path in the context.
Unknown paths raise, so a typo fails the run instead of shipping a blank.
``{# comments #}`` are stripped and never reach the output.
"""

from __future__ import annotations

import re
from typing import Any

from profile_generator.errors import TemplateError

PLACEHOLDER = re.compile(r"\{\{\s*([A-Za-z_][\w.]*)\s*\}\}")
COMMENT = re.compile(r"\{#.*?#\}\n?", re.DOTALL)


def lookup(ctx: dict[str, Any], path: str) -> Any:
    value: Any = ctx
    for part in path.split("."):
        if isinstance(value, dict) and part in value:
            value = value[part]
        else:
            raise KeyError(path)
    return value


def placeholders(template: str) -> list[str]:
    return PLACEHOLDER.findall(COMMENT.sub("", template))


def render(template: str, ctx: dict[str, Any]) -> str:
    template = COMMENT.sub("", template)
    missing = []
    for path in PLACEHOLDER.findall(template):
        try:
            lookup(ctx, path)
        except KeyError:
            missing.append(path)
    if missing:
        raise TemplateError(f"Unknown placeholder(s): {', '.join(sorted(set(missing)))}")
    return PLACEHOLDER.sub(lambda m: str(lookup(ctx, m.group(1))), template)
