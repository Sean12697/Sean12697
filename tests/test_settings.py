import tempfile
import unittest
from pathlib import Path

from profile_generator.settings import Settings, env_example


class SettingsTests(unittest.TestCase):
    def test_precedence(self):
        with tempfile.TemporaryDirectory() as d:
            cfg = Path(d) / "profile.toml"
            cfg.write_text('[settings]\nsteam_games = 3\nsteam_id = "toml"\n')
            env = Path(d) / ".env"
            env.write_text("PROFILE_STEAM_ID=dotenv\nSTEAM_API_KEY='abc'\n")
            s = Settings.load(cfg, env, environ={"PROFILE_STEAM_GAMES": "4"})
            self.assertEqual(s.steam_id, "dotenv")
            self.assertEqual(s.steam_games, 4)
            self.assertEqual(s.steam_api_key, "abc")
            s = Settings.load(cfg, env, environ={}, overrides={"steam_games": 7})
            self.assertEqual(s.steam_games, 7)

    def test_list_and_bool_coercion(self):
        s = Settings.load(
            None,
            None,
            environ={"PROFILE_STEAM_BLOCKED_DESCRIPTORS": "3, 4", "PROFILE_OFFLINE": "yes"},
        )
        self.assertEqual(s.steam_blocked_descriptors, [3, 4])
        self.assertTrue(s.offline)

    def test_unknown_setting_rejected(self):
        with self.assertRaises(ValueError):
            Settings.load(None, None, environ={}, overrides={"nope": 1})

    def test_secrets_masked_and_env_example_has_no_secret(self):
        s = Settings.load(None, None, environ={"STEAM_API_KEY": "secret"})
        self.assertEqual(s.public()["steam_api_key"], "set")
        self.assertIn("PROFILE_STEAM_API_KEY=\n", env_example())
        self.assertNotIn("secret", env_example())

    def test_committed_env_example_is_current(self):
        root = Path(__file__).parent.parent
        self.assertEqual((root / ".env.example").read_text(), env_example() + "\n")
