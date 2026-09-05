# Setup

This section explains
how to add `trcks` to your project,
how to set up a compatible static type checker, and
how to install the `trcks` skill for AI coding agents.

## Adding `trcks` to your project

`trcks` is [available on PyPI](https://pypi.org/project/trcks/).
To be able to import it at runtime (e.g. `import trcks`),
you need to add it to your project as a production dependency.

If you use `uv` to manage your dependencies,
run the following command in your terminal:

```shell
uv add trcks
```

## Setting up a compatible static type checker

`trcks` is compatible with current versions of `mypy`, `pyrefly`, and `pyright`.
For convenience,
`trcks` provides optional dependencies (extras)
for installing compatible versions of these tools.

Since `trcks` is already a production dependency,
you can add the type checker extras as separate dev dependencies.
This way, `trcks` remains in `project.dependencies`
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

1. as part of the `trcks` repository on GitHub and
2. as part of the `trcks` package on PyPI.

### Installing with the GitHub CLI

If you use the GitHub CLI, you can install the skill
directly from the `trcks` repository on GitHub
by running the following command in your terminal:

```shell
gh skill install christophgietl/trcks trcks@0.7.2
```

Please make sure that the version (`0.7.2` in the above example) matches
the version of the `trcks` library used in your project.
Whenever you update the `trcks` library, please update the `trcks` skill as well.

### Installing with the `skills` CLI

If you use Node.js, you can install the skill
directly from the `trcks` repository on GitHub
with the [`skills` CLI](https://skills.sh) by running the following command
in your terminal:

```shell
npx skills add https://github.com/christophgietl/trcks/tree/0.7.2 --skill trcks
```

Please make sure that the version (`0.7.2` in the above example) matches
the version of the `trcks` library used in your project.
Whenever you update the `trcks` library, please update the `trcks` skill as well.

### Installing with Library Skills

If you use `uv`, you can install the skill
from the `trcks` library already installed in your environment
with [Library Skills](https://library-skills.io/)
by running the following command in your terminal:

```shell
uvx library-skills install --skill trcks
```

Alternatively, you can add Library Skills to your project as a dev dependency and
then run the install command:

```shell
uv add --dev library-skills
uv run library-skills install --skill trcks
```

Library Skills scans the dependencies of your project,
finds the skills bundled with the installed libraries, and
adds them to your project as symbolic links.
The installed skill always matches
the version of the `trcks` library used in your project.
Whenever you update the `trcks` library, the skill stays up to date.
