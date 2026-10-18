"""Command line: ``profile-gen render | fetch | check | settings``."""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from profile_generator import __version__
from profile_generator.errors import TemplateError
from profile_generator.generate import build_context, demo_data, generate
from profile_generator.settings import Settings, env_example
from profile_generator.template import placeholders, render


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="profile-gen", description=__doc__)
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    p.add_argument("--config", type=Path, default=Path("profile.toml"), help="settings file")
    p.add_argument("--env-file", type=Path, default=Path(".env"), help="dotenv file")
    p.add_argument("-v", "--verbose", action="store_true", help="debug logging")
    sub = p.add_subparsers(dest="command", required=True)

    def common(sp: argparse.ArgumentParser) -> None:
        sp.add_argument("--offline", action="store_true", default=None, help="use demo data")
        sp.add_argument("--template", type=Path)
        sp.add_argument("--snapshot", type=Path)
        sp.add_argument("--steam-games", type=int)
        sp.add_argument("--timeout", type=float)

    r = sub.add_parser("render", help="fetch data and write the README")
    common(r)
    r.add_argument("--output", type=Path)
    r.add_argument("--stdout", action="store_true", help="print instead of writing files")
    r.add_argument("--strict", action="store_true", default=None, help="fail if a source fails")

    f = sub.add_parser("fetch", help="print the data context as JSON")
    common(f)

    c = sub.add_parser("check", help="validate the template against demo data")
    c.add_argument("--template", type=Path)

    s = sub.add_parser("settings", help="show effective settings")
    s.add_argument("--env-example", action="store_true", help="print a .env.example")
    return p


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(levelname)s %(message)s",
        stream=sys.stderr,
    )
    keys = ("offline", "template", "snapshot", "steam_games", "timeout", "output", "strict")
    overrides = {k: getattr(args, k, None) for k in keys}
    settings = Settings.load(args.config, args.env_file, overrides=overrides)

    if args.command == "settings":
        if args.env_example:
            print(env_example())
        else:
            print(json.dumps(settings.public(), indent=2))
        return 0

    if args.command == "check":
        template = settings.template.read_text(encoding="utf-8")
        try:
            render(template, build_context(demo_data()))
        except TemplateError as exc:
            print(f"template: {exc}", file=sys.stderr)
            return 1
        print(f"template ok: {len(placeholders(template))} placeholders resolve")
        return 0

    if args.command == "fetch":
        from profile_generator.generate import collect

        data, failures = collect(settings)
        print(json.dumps({"data": data, "failures": failures}, indent=2, ensure_ascii=False))
        return 1 if failures and settings.strict else 0

    try:
        result = generate(settings, persist=not args.stdout)
    except TemplateError as exc:
        print(f"template: {exc}", file=sys.stderr)
        return 1
    if args.stdout:
        sys.stdout.write(result.markdown)
    else:
        settings.output.write_text(result.markdown, encoding="utf-8")
        logging.info("wrote %s", settings.output)
    if result.failures and settings.strict:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
