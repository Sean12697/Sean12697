import json
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path

from helpers import FakeHttp, fixture, settings
from test_sources import GAMES, steam_routes

from profile_generator.blocks import badges, games
from profile_generator.cli import main
from profile_generator.generate import generate
from profile_generator.http import HttpError

NOW = datetime(2026, 10, 19, 7, 0, tzinfo=UTC)
STATS_URL = "https://seanomahoney.com/stats.json"


def routes(**overrides):
    r = {STATS_URL: fixture("stats.json"), **steam_routes(GAMES)}
    r.update(overrides)
    return r


class GenerateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.s = settings(self.dir)

    def tearDown(self):
        self.tmp.cleanup()

    def test_full_render(self):
        result = generate(self.s, FakeHttp(routes()), NOW)
        md = result.markdown
        self.assertEqual(result.failures, {})
        self.assertIn("**28** [hackathons]", md)
        self.assertIn("**38** beer festivals", md)
        self.assertIn("**6,000+** unique beers", md)
        self.assertIn("Brand New", md)
        self.assertIn("19 October 2026, 07:00 UTC", md)
        self.assertNotIn("{{", md)
        self.assertNotIn("{#", md)
        snap = json.loads(self.s.snapshot.read_text())
        self.assertEqual(snap["stats"]["hackathons"], 28)

    def test_failed_source_falls_back_to_snapshot(self):
        generate(self.s, FakeHttp(routes()), NOW)
        down = HttpError("x", 503, "down")
        http = FakeHttp(routes(**{STATS_URL: down}))
        result = generate(self.s, http, NOW)
        self.assertIn("stats", result.failures)
        self.assertIn("**28** [hackathons]", result.markdown)

    def test_failed_source_without_snapshot_uses_empty_defaults(self):
        down = HttpError("x", 503, "down")
        http = FakeHttp(routes(**{STATS_URL: down}))
        result = generate(self.s, http, NOW)
        self.assertIn("**many** [hackathons]", result.markdown)
        self.assertNotIn("stats", json.loads(self.s.snapshot.read_text()))

    def test_no_games_message(self):
        self.assertIn("Nothing on Steam", games.render({"steam": {"games": []}}))

    def test_shields_escaping(self):
        url = badges.shield("Unique beers", "6,000+", "FFC000")
        self.assertIn("Unique%20beers-6%2C000%2B-FFC000", url)
        self.assertIn("a--b", badges.shield("a-b", "1", "000"))

    def test_hours_and_bar(self):
        self.assertEqual(games.hours(45), "45 min")
        self.assertEqual(games.hours(90), "1.5 h")
        self.assertEqual(games.hours(6000), "100 h")
        self.assertEqual(games.bar(1, 100), "▰" + "▱" * 9)
        self.assertEqual(games.bar(5, 5), "▰" * 10)


class CliTests(unittest.TestCase):
    def test_check_and_offline_render(self):
        root = Path(__file__).parent.parent
        config, template = str(root / "profile.toml"), str(root / "template.md")
        self.assertEqual(main(["--config", config, "check", "--template", template]), 0)
        with tempfile.TemporaryDirectory() as d:
            out = Path(d) / "README.md"
            args = ["--config", config, "--env-file", str(Path(d) / ".env"), "render"]
            args += ["--offline", "--template", template, "--output", str(out)]
            code = main(args)
            self.assertEqual(code, 0)
            self.assertIn("Hades", out.read_text())
