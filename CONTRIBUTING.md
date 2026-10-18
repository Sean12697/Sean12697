# Contributing

Run `make dev`, then `make lint test check` before pushing. Content changes go in `template.md`; code changes need tests that use `FakeHttp` rather than the network. See [docs/GENERATOR.md](docs/GENERATOR.md) for how the pipeline fits together and how to add a source or block.
