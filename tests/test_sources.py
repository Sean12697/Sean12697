import tempfile
import unittest
from pathlib import Path

from helpers import FakeHttp, fixture, settings

from profile_generator.errors import SourceError
from profile_generator.http import HttpError
from profile_generator.sources import stats, steam


def steam_routes(recent_games, descriptors=None, achievements=None):
    descriptors = descriptors or {}
    achievements = achievements or {}

    def store(params):
        appid = params["appids"]
        ids = descriptors.get(appid, [])
        return {str(appid): {"success": True, "data": {"content_descriptors": {"ids": ids}}}}

    def ach(params):
        rows = achievements.get(params["appid"])
        if rows is None:
            return HttpError(steam.ACHIEVEMENTS_URL, 400, "Requested app has no stats")
        return {"playerstats": {"achievements": rows, "success": True}}

    return {
        steam.RECENT_URL: {"response": {"total_count": len(recent_games), "games": recent_games}},
        steam.STORE_URL: store,
        steam.ACHIEVEMENTS_URL: ach,
    }


GAMES = [
    {"appid": 1, "name": "Old Favourite", "playtime_2weeks": 30, "playtime_forever": 6000},
    {"appid": 2, "name": "Brand New", "playtime_2weeks": 300, "playtime_forever": 300},
    {"appid": 3, "name": "Adult Thing", "playtime_2weeks": 999, "playtime_forever": 999},
]


class StatsTests(unittest.TestCase):
    def test_uses_formatted_beers(self):
        data = stats.parse(fixture("stats.json"))
        self.assertEqual(data["hackathons"], 28)
        self.assertEqual(data["beer_festivals"], 38)
        self.assertEqual(data["beers"], "6,000+")
        self.assertEqual(data["raw"]["content"]["blogPosts"], 32)

    def test_missing_fields_raise(self):
        with self.assertRaises(SourceError):
            stats.parse({"timeline": {"hackathons": 1}})


class SteamTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.s = settings(Path(self.tmp.name))

    def tearDown(self):
        self.tmp.cleanup()

    def test_filters_sorts_and_counts_achievements(self):
        http = FakeHttp(
            steam_routes(
                GAMES,
                descriptors={3: [1, 3, 5]},
                achievements={2: [{"achieved": a} for a in (1, 0, 1, 0)]},
            )
        )
        games = steam.fetch(self.s, http)["games"]
        self.assertEqual([g["name"] for g in games], ["Brand New", "Old Favourite"])
        self.assertTrue(games[0]["is_new"])
        first = games[0]
        self.assertEqual((first["achievements_unlocked"], first["achievements_total"]), (2, 4))
        self.assertIsNone(games[1]["achievements_total"])

    def test_limit(self):
        s = settings(Path(self.tmp.name), steam_games=1)
        games = steam.fetch(s, FakeHttp(steam_routes(GAMES)))["games"]
        self.assertEqual(len(games), 1)

    def test_store_failure_does_not_hide_game(self):
        routes = steam_routes(GAMES[:1])
        routes[steam.STORE_URL] = HttpError(steam.STORE_URL, 429, "rate limited")
        games = steam.fetch(self.s, FakeHttp(routes))["games"]
        self.assertEqual(len(games), 1)

    def test_no_key(self):
        s = settings(Path(self.tmp.name), steam_api_key="")
        with self.assertRaises(SourceError):
            steam.fetch(s, FakeHttp({}))
