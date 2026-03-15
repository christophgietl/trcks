# Setup

This section explains
how to add `trcks` to your project
and how to set up a compatible static type checker.

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

`trcks` is compatible with current versions of `mypy` and `pyright`.
For convenience,
`trcks` provides optional dependencies (extras)
for installing compatible versions of both tools.

Since `trcks` is already a production dependency,
you can add the type checker extras as separate dev dependencies.
This way, `trcks` remains in `project.dependencies`
while the type checker is only installed in development environments.

If you use `uv` and want to use `mypy` as your static type checker,
run the following command in your terminal:

```shell
uv add --dev "trcks[mypy]"
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
    "trcks==0.4.2",
]
```
