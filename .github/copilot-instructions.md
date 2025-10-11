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
- Type aliases in `_typing.py` handle Python version compatibility (3.10-3.14)
- Core types are intentionally simple tuples for maximum interoperability
- No inheritance hierarchy - composition over inheritance throughout

### Architecture decisions

**Type safety philosophy**: The library encourages encoding domain errors
in function signatures via `Result[ErrorType, SuccessType]`.
This makes expected failures explicit and type-checkable rather than using exceptions.

**Dual API design**: The library intentionally provides two equivalent ways
to work with railway-oriented programming:
- OOP style for developers comfortable with method chaining (similar to pandas, requests)
- FP style for developers preferring function composition (similar to toolz, returns)

**Wrapper pattern**:
All OOP classes (`Wrapper`, `ResultWrapper`, `AwaitableWrapper`, etc.) are
lightweight containers that hold a `core` value and provide type-safe method chaining.
They never mutate - each method returns a new wrapper instance.

**Pipeline composition**:
FP style uses explicit pipeline tuples `(input, func1, func2, ...)`
rather than function decorators or complex combinators.
This makes type inference easier and debugging more transparent.

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

### Module organization and import patterns

**Core imports** (always needed):

```python
from trcks import Result, AwaitableResult  # Core types
```

**OOP style imports**:

```python
from trcks.oop import Wrapper, ResultWrapper, AwaitableWrapper, AwaitableResultWrapper
# Use Wrapper(core=value) as entry point for method chaining
```

**FP style imports**:

```python
from trcks.fp.composition import pipe, compose, Pipeline2, Pipeline3  # etc.
from trcks.fp.monads import result as r, awaitable as a, awaitable_result as ar
# Convention: alias monad modules with single letters for conciseness
```

**Module responsibilities**:
- `src/trcks/__init__.py`: Core types (`Result`, `Success`, `Failure`) and type aliases
- `src/trcks/_typing.py`: Python version compatibility shims for typing features
- `src/trcks/oop.py`:
    All wrapper classes with extensive method chaining API (2600+ lines)
- `src/trcks/fp/composition.py`:
    Pipeline types (`Pipeline1` through `Pipeline8`) and composition functions
- `src/trcks/fp/monads/result.py`:
    Functional operations on `Result` types (`map_success`, `map_failure`, etc.)
- `src/trcks/fp/monads/awaitable.py`: Operations on `Awaitable` types
- `src/trcks/fp/monads/awaitable_result.py`: Operations on `AwaitableResult` types

**Import conventions**:
- Never import `*` - all imports are explicit
- Type imports typically use `TypeAlias` annotations
- Monad modules conventionally aliased as single letters in FP style
- Pipeline types are numbered by arity: `Pipeline2[T0, T1, T2]` for input + 2 functions

## Development workflow

### Build system & dependencies

- **Package manager**: `uv` (required version >= 0.8, < 0.9)
- **Build backend**: `pdm-backend` with SCM versioning from Git tags
- **Dev dependencies**: All in `[dependency-groups.dev]` in `pyproject.toml`
- **Import linter**: `import-linter` is used to enforce
    import rules within and between Python packages.
    Its contracts are configured in `pyproject.toml`.

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

# Enforce import rules
uv run lint-imports
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
