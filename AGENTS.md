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
  `tuple`-based type with literal discriminants ("success" and "failure");
  lets functions return domain errors instead of raising them.
- Combinations with `collections.abc.Awaitable` and `tuple` for different use cases
  (e.g. `trcks.AwaitableResultTuple[FailureType, SuccessType]`).

### Exception types defined in `trcks.exceptions`

- The module `trcks.exceptions` provides exception classes for `trcks`
  (e.g. `trcks.exceptions.TrcksTypeError`).

### Wrapper classes defined in `trcks.oop`

- The package `trcks.oop` provides wrapper classes for OOP-style method chaining
  (e.g. `trcks.oop.Wrapper`, `trcks.oop.AwaitableWrapper`, `trcks.oop.ResultWrapper`,
  `trcks.oop.AwaitableResultWrapper`, `trcks.oop.TupleWrapper`, `trcks.oop.ResultTupleWrapper`,
  `trcks.oop.AwaitableTupleWrapper`, `trcks.oop.AwaitableResultTupleWrapper`).
- All wrapper classes are designed to be lightweight and immutable.
- All wrapper class methods return new wrapper instances.

### Pipelines and monads defined in `trcks.fp`

- The module `trcks.fp.composition` provides
  higher-order functions for composing functions
  (e.g. `trcks.fp.composition.pipe` and `trcks.fp.composition.compose`).
- The package `trcks.fp.monads` provides type-specific mapping functions
  for `collections.abc.Awaitable`, `trcks.Result`, `tuple`,
  `trcks.AwaitableResult`, `trcks.AwaitableTuple`, `trcks.ResultTuple` and
  `trcks.AwaitableResultTuple` values.

## Code style

- Give every module a `__docformat__ = "google"` dunder.
- Place all module dunders after imports, including imports inside
  `if TYPE_CHECKING:` blocks.
- Sort module dunders alphabetically (e.g. `__all__` before `__docformat__`).
- Sort functions alphabetically within each module.
- Sort classes alphabetically within each module.
- Sort methods alphabetically within each class.
- Use the following import patterns across code and documentation:

  ```pycon
  >>> # Generic types from the main package:
  >>> from trcks import (
  ...     AwaitableResult,
  ...     AwaitableResultTuple,
  ...     Failure,
  ...     Result,
  ...     ResultTuple,
  ... )
  >>> # OOP wrapper classes:
  >>> from trcks.oop import (
  ...     AwaitableResultTupleWrapper,
  ...     AwaitableResultWrapper,
  ...     AwaitableTupleWrapper,
  ...     AwaitableWrapper,
  ...     ResultTupleWrapper,
  ...     ResultWrapper,
  ...     TupleWrapper,
  ...     Wrapper,
  ... )
  >>> # FP composition helpers:
  >>> from trcks.fp.composition import Composable, Pipeline3, compose, pipe
  >>> # FP monads (with single-letter aliases for conciseness):
  >>> from trcks.fp.monads import (
  ...     awaitable as a,
  ...     awaitable_result as ar,
  ...     awaitable_result_tuple as art,
  ...     awaitable_tuple as at,
  ...     identity as i,
  ...     result as r,
  ...     result_tuple as rt,
  ...     tuple_ as t,
  ... )

  ```

## Development tools

`trcks` uses `uv` for managing dependencies and tools.

```shell
# Run linting and code formatting:
uv run pre-commit run --all-files
# Run static type checks:
uv run --all-extras mypy
uv run --all-extras pyrefly check
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

- Every public function in `src/trcks/`
  (except for property methods and dunder methods)
  must have a docstring with ≥1 example (run as doctest by `pytest`);
  reuse example functions from existing doctests.
- `pytest` also collects "pycon" blocks in `**/*.md` and `tests/trcks/**/test_*.py`
  (mirroring `src/trcks/`).
- 100% coverage required; mark unreachable code with `# pragma: no cover`
  (not needed for `if TYPE_CHECKING` blocks).

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
