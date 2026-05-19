# AI coding agent instructions for `trcks`

## Project requirements

- `trcks` is a Python library for type-safe railway-oriented programming (ROP).
- `trcks` encourages returning domain errors instead of raising them.
- `trcks` provides generic return types for synchronous and asynchronous functions.
- `trcks` supports two distinct but equivalent programming styles:
  - OOP style for developers comfortable with method chaining
  - FP style for developers preferring function composition

## Architecture decisions

### Return types defined in `trcks`

- `trcks.Result[FailureType, SuccessType]`:
  a `tuple`-based type with literal discriminants ("success"/"failure")
  for type-safe pattern matching;
  allows functions to return either
  a domain error (`FailureType`) or a success value (`SuccessType`)
  without raising exceptions.
- `trcks.AwaitableResult[FailureType, SuccessType]`:
  an alias for `collections.abc.Awaitable[trcks.Result[FailureType, SuccessType]]`
  for annotating asynchronous functions.

### Wrapper classes defined in `trcks.oop`

- The module `trcks.oop` provides wrapper classes for OOP-style method chaining
  (e.g. `trcks.oop.Wrapper`, `trcks.oop.ResultWrapper`).
- All wrapper classes are designed to be lightweight and immutable.
- All wrapper class methods return new wrapper instances.

### Pipelines and monads defined in `trcks.fp`

- The module `trcks.fp.composition` provides
  higher-order functions for composing functions
  (e.g. `trcks.fp.composition.pipe` and `trcks.fp.composition.compose`).
- The package `trcks.fp.monads` provides type-specific mapping functions
  for `trcks.Result`, `collections.abc.Awaitable` and `trcks.AwaitableResult` values.

### Providing typing features to all supported Python versions in `trcks._typing`

- `trcks._typing` provides recent features from Python's `typing` library.
- `trcks._typing` can be used by all supported Python versions.

## Code style

Use the following import patterns across code and documentation:

```pycon
>>> # Generic types from the main package:
>>> from trcks import AwaitableResult, Result
>>> # OOP wrapper classes:
>>> from trcks.oop import AwaitableResultWrapper, ResultWrapper, Wrapper
>>> # FP composition helpers:
>>> from trcks.fp.composition import Composable, Pipeline3, compose, pipe
>>> # FP monads (with single-letter aliases for conciseness):
>>> from trcks.fp.monads import awaitable as a, awaitable_result as ar

```

## Development tools

`trcks` uses `uv` for managing dependencies and tools.

```shell
# Run linting and code formatting:
uv run pre-commit run --all-files
# Run static type checks:
uv run --all-extras mypy
uv run --all-extras pyright
# Run unit tests and doctests:
uv run pytest
# Enforce rules for the imports within and between Python packages:
uv run import-linter lint
# Generate documentation:
uv run mkdocs build
# Build distribution package:
uv build
```

## Testing strategy

- Each function in `src/trcks/` must have a docstring with at least one example
  (run as doctest by `pytest`).
- `pytest` also collects all "pycon" code blocks in `**/*.md` files and
  all `tests/trcks/**/test_*.py` files (mirroring `src/trcks/`).
- Test coverage must be 100%; unreachable code and `if TYPE_CHECKING` blocks
  must be marked with `# pragma: no cover`.

## Documentation requirements

- The documentation website is built with Material for MkDocs,
  configured in `mkdocs.yml` and written in `docs/**/*.md`.
- Update `mkdocs.yml` and `docs/**/*.md` whenever features, architecture or UI change.
- API docs in `docs/reference/trcks.*.md` must mirror
  the module and class structure of `trcks`
  (e.g. `trcks.fp.monads.result` → `docs/reference/trcks.fp.monads.result.md`).
  Create, delete or rename these files to match module or class changes.
- Keep `AGENTS.md` up to date when architecture or tooling changes.
- Keep `CONTRIBUTING.md` up to date when tooling changes.
- Keep `README.md` up to date when features or UI changes.
