# Contributing to `trcks`

Thank you for considering contributing to `trcks`!
The following section describes how to set up and use a development environment.

## Development environment

`trcks` uses the following developer tools:

- [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) for generating documentation
- [mypy](https://mypy.readthedocs.io) for static type checking
- [pre-commit](https://pre-commit.com) for managing pre-commit hooks (particularly for code formatting and linting)
- [pyright](https://microsoft.github.io/pyright/) for static type checking
- [pytest](https://pytest.org) for unit testing and doctests
- [uv](https://docs.astral.sh/uv/) for dependency management and packaging

Moreover, `trcks` uses [GitHub Actions](https://github.com/features/actions) for:

- continuous integration (CI)
- publication

### Setup

Please follow these steps to set up your development environment:

1. Install `uv` if you have not already done so.
2. Clone the `trcks` repository and `cd` into it.
3. Install `trcks` and its (development) dependencies by running `uv sync`.
4. Set up the hooks by executing `uv run pre-commit install`.
   The output should look something like this:

   ```plain
   pre-commit installed at .git/hooks/commit-msg
   pre-commit installed at .git/hooks/pre-commit
   ```

### Usage

Run unit tests and doctests:

```shell
uv run pytest
```

Run static type checks:

```shell
uv run mypy
uv run pyright
```

Run pre-commit hooks:

```shell
uv run pre-commit run --all-files
```

Generate documentation:

```shell
uv run mkdocs build
```

Build distribution package:

```shell
uv build
```
