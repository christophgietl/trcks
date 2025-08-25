# AI coding agent instructions for trcks

## Project overview

`trcks` is a Python library for type-safe railway-oriented programming (ROP),
providing two distinct programming styles:

- **Object-oriented style**: Method chaining with wrapper classes (`trcks.oop`)
- **Functional style**: Function composition with pipelines (`trcks.fp`)

Both styles work with the core `Result[F, S]` type -
a discriminated union of `("success", value)` and `("failure", error)` tuples.

## Architecture patterns

### Core type system

- `Result[F, S]` is the fundamental type: `Union[("failure", F), ("success", S)]`
- `AwaitableResult[F, S]` for async operations
- All types are strict tuples with literal "success"/"failure" discriminants
- Type aliases in `_typing.py` handle Python version compatibility (3.9-3.13)

### Dual programming models

**OOP style** (`src/trcks/oop.py`):

```python
result = (
    Wrapper(core=value)
    .map_to_result(validator_func)
    .map_success(transform_func)
    .core
)
```

**FP style** (`src/trcks/fp/`):

```python
pipeline = (input_value, func1, r.map_success(func2), r.map_success_to_result(func3))
result = pipe(pipeline)
```

### Module organization

- `src/trcks/__init__.py`: Core types and type aliases
- `src/trcks/oop.py`: Wrapper classes (2600+ lines, extensive method chaining API)
- `src/trcks/fp/composition.py`: Pipeline types and `pipe()`/`compose()` functions
- `src/trcks/fp/monads/`:
    Monad operations for different types (result, awaitable, etc.)

## Development workflow

### Build system & dependencies

- **Package manager**: `uv` (required version >= 0.8, < 0.9)
- **Build backend**: `pdm-backend` with SCM versioning from Git tags
- **Dev dependencies**: All in `[dependency-groups.dev]` in `pyproject.toml`

### Key commands

```bash
# Install dependencies and sync environment
uv sync

# Run tests with coverage (must be 100%)
uv run pytest

# Build documentation
uv run mkdocs build

# Lint and format
uv run ruff check
uv run ruff format

# Type checking
uv run mypy
uv run pyright
```

### Testing conventions

- **Location**: `tests/` mirrors `src/trcks/` structure
- **Coverage**: 100% required (`--cov-fail-under=100`)
- **Doctest**: Enabled for `.md` files (`--doctest-glob='*.md'`)
- **Async**: Auto mode with function-scoped event loops
- **Test data**: Extensive use of `Final` tuples for test cases
    (see `_FLOATS`, `_OBJECTS`, `_RESULTS` in `test_oop.py`)

## Code quality standards

### Type safety

- `typeCheckingMode = "strict"` in Pyright
- Extensive use of `TypeVar`, `TypeAlias`, and generic constraints
- Cross-version compatibility handled in `_typing.py`
- Use `assert_type()` in tests for type verification

### Style guidelines

- **Ruff**: "ALL" rules selected with specific ignores
- **Docstrings**: Google convention required
- **Import sorting**: Automatic via Ruff
- **Line length**: Standard (not explicitly configured)

### Documentation

- **API docs**: Auto-generated via `mkdocstrings` with cross-references
- **Examples**: Extensive doctests in modules and README
- **Structure**: MkDocs Material with detailed navigation in `mkdocs.yml`

## Testing patterns

### Wrapper class testing

Test both return values AND intermediate wrapper types:

```python
wrapper: Wrapper[float] = Wrapper(core=x)
result_wrapper: ResultWrapper[Error, float] = wrapper.map_to_result(validator)
final_result: Result[Error, float] = result_wrapper.core
```

### Async testing

Use consistent patterns for testing async wrapper classes:

```python
async def test_async_wrapper():
    awaitable_wrapper = AwaitableWrapper(core=async_func(value))
    result = await awaitable_wrapper.map(sync_transform).core
```

## Critical implementation details

### Error handling philosophy

- Errors are **values**, not exceptions
- Use `Result[ErrorType, SuccessType]` instead of raising exceptions
- Domain errors become part of function signatures via type system

### Performance considerations

- Wrapper classes are lightweight - primarily type-safe method chaining
- Function composition in FP style has minimal overhead
- Extensive use of generics enables static optimization

### Integration points

- Cross-references to functional programming libraries (returns, expression) in docs
- Designed for interoperability with standard Python async patterns
- Compatible with static type checkers (mypy, pyright, pylance)
