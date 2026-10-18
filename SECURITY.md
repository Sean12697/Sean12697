# Security

The only secret is the Steam Web API key. It is read from the `STEAM_API_KEY` repository secret in Actions or from a local `.env`, never from `profile.toml`, and the HTTP client never logs query strings, where Steam expects the key. Report a vulnerability privately to sean@inevitableteam.com rather than opening a public issue.
