# Setup

This section explains
how to add `trcks` to your project,
set up a compatible static type checker, and
install the `trcks` skill for AI coding agents.

## Adding `trcks` to your project

`trcks` is [available on PyPI](https://pypi.org/project/trcks/).
To import it at runtime (e.g. `import trcks`),
add it to your project as a production dependency.

If you use `uv`, run the following command in your terminal:

```shell
uv add trcks
```

## Setting up a compatible static type checker

`trcks` is compatible with current versions of `mypy`, `pyrefly`, and `pyright`.
For convenience,
`trcks` provides optional dependencies (extras)
for installing compatible versions of these tools.

Since `trcks` is already a production dependency,
add the type checker extras as dev dependencies.
This keeps `trcks` in `project.dependencies`
while the type checker is only installed in development environments.

If you use `uv` and want to use `mypy` as your static type checker,
run the following command in your terminal:

```shell
uv add --dev "trcks[mypy]"
```

If you use `uv` and want to use `pyrefly` as your static type checker,
run the following command in your terminal:

```shell
uv add --dev "trcks[pyrefly]"
```

If you use `uv` and want to use `pyright` as your static type checker,
run the following command in your terminal:

```shell
uv add --dev "trcks[pyright]"
```

Your `pyproject.toml` will then look similar to this
(with `trcks` in both `project.dependencies` and `dependency-groups.dev`):

```toml
[dependency-groups]
dev = [
    "trcks[pyright]",
]

[project]
dependencies = [
    "trcks",
]
```

## Installing the `trcks` skill for AI coding agents

`trcks` ships an [agent skill](https://agentskills.io/home)
that teaches AI coding agents how to use `trcks` for railway-oriented programming.
The skill is distributed via two channels:
the `trcks` repository on GitHub and the `trcks` package on PyPI.

### Installing with the GitHub CLI

If you use the GitHub CLI, install the skill
by running the following command in your terminal:

```shell
gh skill install christophgietl/trcks trcks@0.7.2
```

Replace `0.7.2` with the version of the `trcks` library used in your project,
and update the skill whenever you update the library.

### Installing with the `skills` CLI

If you use Node.js, install the skill
with the [`skills` CLI](https://skills.sh)
by running the following command in your terminal:

```shell
npx skills add https://github.com/christophgietl/trcks/tree/0.7.2 --skill trcks
```

Replace `0.7.2` with the version of the `trcks` library used in your project,
and update the skill whenever you update the library.

### Installing with Library Skills

If you use `uv`, install the skill
with [Library Skills](https://library-skills.io/)
by running the following command in your terminal:

```shell
uvx library-skills install --skill trcks
```

Alternatively, add Library Skills as a dev dependency and run the install command:

```shell
uv add --dev library-skills
uv run library-skills install --skill trcks
```

Library Skills scans the dependencies of your project,
finds the skills bundled with the installed libraries, and
adds them to your project as symbolic links.
The skill always matches the installed `trcks` version and stays up to date.
