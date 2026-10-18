# Ideas

A decision record of ideas beyond the brief. Each round keeps its ideas and their status.

## Round 1: v0.1.0

The brief: move the generator into Sean12697/Sean12697, read hackathons, beer festivals and Untappd beers from stats.json, make it modular (Python), and improve the layout, including recently played games.

| Idea | Description | Value | Effort | Status |
| :-- | :-- | :-- | :-- | :-- |
| Single repository | Generator and profile together, committing with `GITHUB_TOKEN` | High | Low | Built |
| stats.json source | One request replaces the Untappd API and HTML scraping | High | Low | Built |
| Steam game table | Cover art, two-week and total playtime, achievement bar, "new" marker | High | Low | Built |
| Template check | Fail on unknown placeholders before pushing | Medium | Low | Built |
| Collapsible history | Fold standby, previous and university roles into `<details>` | Medium | Low | Built |
| Dependency-free runtime | Standard library only, so the Action installs in seconds | Medium | Low | Built |
| Blog feed block | Latest posts from seanomahoney.com/rss.xml | High | Low | Proposed (recommended) |
| Recent Untappd check-ins | Last few beers with labels, using the public RSS or a stats.json extension | High | Medium | Proposed (recommended) |
| Upcoming events | Next hackathon, festival or talk from the portfolio timeline | High | Medium | Proposed (recommended) |
| More stats.json badges | Blog posts, projects, check-ins, years active from `stats.raw` | Medium | Low | Proposed |
| GitHub activity block | Recent public repos, PRs or contribution streak via the GitHub API | Medium | Low | Proposed |
| Pinned projects | Featured projects from stats.json or the portfolio | Medium | Medium | Proposed |
| Light and dark images | `<picture>` with `prefers-color-scheme` sources for badges and art | Medium | Low | Proposed |
| SVG summary card | One generated SVG stat card committed to the repo instead of shields.io | Medium | Medium | Proposed |
| Year in numbers | Hackathons and festivals per year from `timeline.byYear` as a sparkline | Medium | Medium | Proposed |
| Now playing badge | Show the currently running Steam game if any | Low | Low | Proposed |
| Achievement icons | Recent unlocked achievement icons per game (the old code started this) | Low | Medium | Proposed |
| Change-only commits | Commit only when data changes, plus a monthly keepalive | Low | Low | Rejected: daily footer commits already keep the schedule alive with fewer moving parts |
| Section order in settings | Assemble sections from settings rather than one template | Low | Medium | Rejected: a single template is easier to edit and reason about |
| Failure alert | Open an issue when a source has fallen back for several days | Medium | Low | Proposed |
| Untappd stats direct | Call the Untappd API as a second source of truth | Low | Medium | Rejected: stats.json is the agreed single source |
| Localised dates | Footer date in the reader's timezone | Low | High | Rejected: README is static |
| Portfolio parity | Generate the same blocks for seanomahoney.com from this package | Low | High | Proposed |
