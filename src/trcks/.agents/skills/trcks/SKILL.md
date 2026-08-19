---
name: trcks
description: 'Railway-oriented programming (ROP) in Python with the trcks library: Result/Success/Failure types, trcks.oop wrapper classes (Wrapper, ResultWrapper, AwaitableResultWrapper, TupleWrapper, ResultTupleWrapper, AwaitableTupleWrapper, AwaitableResultTupleWrapper), and trcks.fp composition and monads (pipe, compose, trcks.fp.monads.result, awaitable_result, tuple_, result_tuple, awaitable, awaitable_tuple, awaitable_result_tuple, identity). Use when writing, reviewing, or debugging code that returns or consumes trcks Result types, chains map* or tap* calls, converts exception-based error handling to railway-oriented programming, chooses between the trcks OOP and FP style, or hits mypy, pyright, or pyrefly type errors involving trcks generics.'
---

# Railway-oriented programming with `trcks`

`trcks` is a Python library for type-safe railway-oriented programming (ROP).
Instead of raising exceptions for domain errors, functions return a
`trcks.Result[F, S]` value that is either a failure or a success, so a static
type checker (mypy, pyright, or pyrefly) can verify that every caller handles
both outcomes.

`trcks` supports two equivalent styles. Pick one and stay consistent within a
codebase:

- **OOP style** (`trcks.oop`): wrap a value, chain `.map*`/`.tap*` method
  calls, then unwrap it.
- **FP style** (`trcks.fp`): build a pipeline tuple of a start value and
  functions, then run it with `trcks.fp.composition.pipe`.

If the target project already imports `trcks.oop` or `trcks.fp`, match its
existing style. Otherwise, ask the user, or default to the OOP style, which
tends to read more naturally to developers coming from method chaining.

## When (not) to use `trcks`

Use `trcks.Result` for **domain errors** that callers are expected to handle:
"user not found", "validation failed", "insufficient balance", and so on.

Do not replace every raised exception with `trcks.Result`. Programming errors
(bugs), truly unrecoverable failures, and rare edge cases are often better
served by raising an exception, not catching an exception, or returning an
optional value instead. See Scott Wlaschin's
[Against Railway-Oriented Programming](https://fsharpforfunandprofit.com/posts/against-railway-oriented-programming/)
for scenarios where a result type is not the right tool.

## Core vocabulary

- **`trcks.Failure[F]`**: a 2-tuple `("failure", f)` where `f: F`.
- **`trcks.Success[S]`**: a 2-tuple `("success", s)` where `s: S`.
- **`trcks.Result[F, S]`**: the union of `Failure[F]` and `Success[S]`;
  the standard return type for a function that can fail.
- **Single-track**: a plain value that carries no success-or-failure
  information.
- **Double-track**: a `trcks.Result` value: one track for success, one for
  failure.
- **Short-circuiting**: once a step in a chain or pipeline produces a
  failure, later `map_success*`/`tap_success*` steps are skipped and the
  failure flows through to the end unchanged.
- **`map*` (mapping helper)**: applies a function to a wrapped value or
  turns a function into a pipeline step. Forwards any extra positional and
  keyword arguments to the given function, so a lambda or `functools.partial`
  is not needed just to bind an extra argument.
- **`tap*`**: runs a side effect (logging, I/O) and returns the original
  value unchanged, instead of the side effect's own (often `None`) return
  value.
- **Homogeneous tuple**: a `tuple[T, ...]` whose elements share one type,
  processed element-wise by the `*_tuple` wrapper classes and monad modules.
- **Layering order**: `trcks` only models `Awaitable > Result > tuple` (and
  its subsequences), matching how a conventional `async def` function that
  raises and returns a tuple behaves: await first, then get success-or-failure,
  then get the tuple elements. It does not provide the reverse orderings
  (e.g. `Result > Awaitable > tuple`).

## Picking the right building block

Match the runtime shape of the code (sync or async, single value or
homogeneous tuple) and the track (single-track or double-track) to one
`trcks.oop` wrapper class and its equivalent `trcks.fp.monads` module:

| Runtime and track       | Single value: `trcks.oop` / `trcks.fp`                  | Homogeneous tuple: `trcks.oop` / `trcks.fp`                          |
|--------------------------|----------------------------------------------------------|------------------------------------------------------------------------|
| Sync, single-track       | `Wrapper` / `trcks.fp.composition.pipe` + `identity`      | `TupleWrapper` / `tuple_`                                              |
| Sync, double-track       | `ResultWrapper` / `result`                                | `ResultTupleWrapper` / `result_tuple`                                  |
| Async, single-track      | `AwaitableWrapper` / `awaitable`                          | `AwaitableTupleWrapper` / `awaitable_tuple`                           |
| Async, double-track      | `AwaitableResultWrapper` / `awaitable_result`             | `AwaitableResultTupleWrapper` / `awaitable_result_tuple`               |

All `trcks.fp.monads` modules are conventionally imported with single-letter
aliases:

```python
from trcks.fp.monads import (
    awaitable as a,
    awaitable_result as ar,
    awaitable_result_tuple as art,
    awaitable_tuple as at,
    identity as i,
    result as r,
    result_tuple as rt,
    tuple_ as t,
)
```

## OOP quick start

Wrap the input in a `trcks.oop.Wrapper`, chain `map*`/`tap*` method calls, and
read `.core` to unwrap the final value:

```pycon
>>> from typing import Literal
>>> from trcks import Result
>>> from trcks.oop import Wrapper
>>>
>>> UserDoesNotExist = Literal["User does not exist"]
>>> UserDoesNotHaveASubscription = Literal["User does not have a subscription"]
>>> FailureDescription = UserDoesNotExist | UserDoesNotHaveASubscription
>>>
>>> def get_user_id(user_email: str) -> Result[UserDoesNotExist, int]:
...     if user_email == "erika.mustermann@domain.org":
...         return "success", 1
...     if user_email == "john_doe@provider.com":
...         return "success", 2
...     return "failure", "User does not exist"
...
>>> def get_subscription_id(
...     user_id: int
... ) -> Result[UserDoesNotHaveASubscription, int]:
...     if user_id == 1:
...         return "success", 42
...     return "failure", "User does not have a subscription"
...
>>> def get_subscription_fee(subscription_id: int) -> float:
...     return subscription_id * 0.1
...
>>> def get_subscription_fee_by_email(
...     user_email: str
... ) -> Result[FailureDescription, float]:
...     return (
...         Wrapper(core=user_email)
...         .map_to_result(get_user_id)
...         .map_success_to_result(get_subscription_id)
...         .map_success(get_subscription_fee)
...         .core
...     )
...
>>> get_subscription_fee_by_email("erika.mustermann@domain.org")
('success', 4.2)
>>> get_subscription_fee_by_email("john_doe@provider.com")
('failure', 'User does not have a subscription')
>>> get_subscription_fee_by_email("jane_doe@provider.com")
('failure', 'User does not exist')

```

`ResultWrapper` (the type of `Wrapper(...).map_to_result(...)`) provides a
`map_failure*`/`map_success*` and `tap_failure*`/`tap_success*` method for
every `map*`/`tap*` method of `Wrapper`. The most commonly used ones:

| Method | Purpose |
|---|---|
| `.map(f)` | Apply a plain function to a plain (single-track) value. |
| `.map_to_result(f)` | Apply a `Result`-returning function, switching to double-track. |
| `.map_success(f)` | Apply a plain function to the success value only. |
| `.map_success_to_result(f)` | Apply a `Result`-returning function to the success value only. |
| `.map_failure(f)` | Apply a plain function to the failure value only. |
| `.tap(f)` / `.tap_success(f)` / `.tap_failure(f)` | Run a side effect, keep the original value. |
| `.map_success_to_awaitable_result(f)` | Apply an async `Result`-returning function; switches to `AwaitableResultWrapper`. |
| `.core` | Unwrap the final value. |

## FP quick start

Build a pipeline tuple of a start value and functions, then run it with
`trcks.fp.composition.pipe`. Use `trcks.fp.monads.result` (aliased `r`) to
turn plain functions into functions that operate on the success or failure
side of a `Result`:

```pycon
>>> from typing import Literal
>>> from trcks import Result
>>> from trcks.fp.composition import Pipeline3, pipe
>>> from trcks.fp.monads import result as r
>>>
>>> UserDoesNotExist = Literal["User does not exist"]
>>> UserDoesNotHaveASubscription = Literal["User does not have a subscription"]
>>> FailureDescription = UserDoesNotExist | UserDoesNotHaveASubscription
>>>
>>> def get_user_id(user_email: str) -> Result[UserDoesNotExist, int]:
...     if user_email == "erika.mustermann@domain.org":
...         return "success", 1
...     if user_email == "john_doe@provider.com":
...         return "success", 2
...     return "failure", "User does not exist"
...
>>> def get_subscription_id(
...     user_id: int
... ) -> Result[UserDoesNotHaveASubscription, int]:
...     if user_id == 1:
...         return "success", 42
...     return "failure", "User does not have a subscription"
...
>>> def get_subscription_fee(subscription_id: int) -> float:
...     return subscription_id * 0.1
...
>>> def get_subscription_fee_by_email(
...     user_email: str
... ) -> Result[FailureDescription, float]:
...     # Explicitly assigning a type to `pipeline` might
...     # help your static type checker understand that
...     # `pipeline` is a valid argument for `pipe`:
...     pipeline: Pipeline3[
...         str,
...         Result[UserDoesNotExist, int],
...         Result[FailureDescription, int],
...         Result[FailureDescription, float],
...     ] = (
...         user_email,
...         get_user_id,
...         r.map_success_to_result(get_subscription_id),
...         r.map_success(get_subscription_fee),
...     )
...     return pipe(pipeline)
...
>>> get_subscription_fee_by_email("erika.mustermann@domain.org")
('success', 4.2)
>>> get_subscription_fee_by_email("john_doe@provider.com")
('failure', 'User does not have a subscription')
>>> get_subscription_fee_by_email("jane_doe@provider.com")
('failure', 'User does not exist')

```

A `Pipeline` is a tuple of a start value followed by up to seven compatible
functions (`trcks.fp.composition.Pipeline0` through `Pipeline7`); annotating
the pipeline variable's type (as above) helps a static type checker confirm
that it is a valid argument for `pipe`. `trcks.fp.composition.compose` builds
a reusable function out of a pipeline without a start value, instead of
running one immediately.

Each `trcks.fp.monads` module follows the same naming convention as `result`:
`map_failure`/`map_success` apply a function on one side of the `Result`;
`map_failure_to_result`/`map_success_to_result` apply a `Result`-returning
function; `tap_failure`/`tap_success` run a side effect and keep the
original value.

## Async code

An `async def ... -> T` function actually returns `collections.abc.Awaitable[T]`,
and an `async def ... -> Result[F, S]` function returns
`trcks.AwaitableResult[F, S]` (an alias for `Awaitable[Result[F, S]]`).

- OOP: `Wrapper.map_to_awaitable(f)` and `Wrapper.map_to_awaitable_result(f)`
  switch to `AwaitableWrapper`/`AwaitableResultWrapper`; `.tap_to_awaitable(f)`
  runs an async side effect. `AwaitableWrapper`/`AwaitableResultWrapper` also
  provide plain `.map`/`.map_success`/etc. for mixing in synchronous steps.
- FP: `trcks.fp.monads.awaitable` (aliased `a`) and
  `trcks.fp.monads.awaitable_result` (aliased `ar`) provide the matching
  `map_to_awaitable`/`map_success_to_awaitable_result`/etc. higher-order
  functions.
- On Python versions older than 3.14, `asyncio.run` requires a
  `collections.abc.Coroutine`, not just an `Awaitable`. Use
  `AwaitableWrapper.core_as_coroutine`/`AwaitableResultWrapper.core_as_coroutine`
  (OOP) or `awaitable.to_coroutine`/`awaitable_result.to_coroutine_result`
  (FP) to convert before calling `asyncio.run`.

## Homogeneous tuples

When the success value (or the single-track value) is a `tuple[T, ...]`
whose elements should each be mapped individually, reach for the
`*_tuple`-flavored building blocks instead of a plain `Result[F, list[S]]`:

- Types: `trcks.SuccessTuple[S]`, `trcks.ResultTuple[F, S]`,
  `trcks.AwaitableTuple[T]`, `trcks.AwaitableResultTuple[F, S]`.
- OOP: `TupleWrapper`, `ResultTupleWrapper`, `AwaitableTupleWrapper`,
  `AwaitableResultTupleWrapper`.
- FP: `trcks.fp.monads.tuple_` (`t`), `result_tuple` (`rt`),
  `awaitable_tuple` (`at`), `awaitable_result_tuple` (`art`).
- These use plural method/function names for element-wise application, e.g.
  `.map_successes(f)`/`map_successes(f)` apply `f` to every success element,
  while `.map_success(f)`/`map_success(f)` (singular) would apply `f` to the
  whole tuple at once.

## OOP ↔ FP cheat sheet

| Operation | `trcks.oop` | `trcks.fp` |
|---|---|---|
| Wrap a value | `Wrapper(core=x)` | start value of a `pipe(...)` call |
| Map a plain value | `.map(f)` | `pipe((x, f))` |
| Map success to `Result` | `.map_success_to_result(f)` | `r.map_success_to_result(f)` |
| Map on success | `.map_success(f)` | `r.map_success(f)` |
| Map on failure | `.map_failure(f)` | `r.map_failure(f)` |
| Side effect on success | `.tap_success(f)` | `r.tap_success(f)` |
| Failable side effect on success | `.tap_success_to_result(f)` | `r.tap_success_to_result(f)` |
| Async success step | `.map_success_to_awaitable_result(f)` | `ar.map_success_to_awaitable_result(f)` |
| Unwrap the result | `.core` | result of `pipe(...)` |

## Common pitfalls

- Do not invent a `Result > Awaitable > tuple` (or similar) permutation;
  `trcks` only supports `Awaitable > Result > tuple` and its subsequences.
- `trcks` is compatible with current versions of `mypy`, `pyrefly`, and
  `pyright`. Add it with `uv add trcks`, and add a type checker as a dev
  dependency with `uv add --dev "trcks[mypy]"` (or `pyrefly`/`pyright`).
- `map*`/`tap*` calls forward extra positional and keyword arguments to the
  given function, so prefer `.map_success(f, extra_arg)` over
  `.map_success(lambda x: f(x, extra_arg))`.
- Do not call a `map_success*`/`tap_success*` method or function on a value
  that is not a `Result`; use the plain `.map`/`.tap` (or `identity.tap`)
  variants for single-track values.

## Further reading

- [Documentation site](https://christophgietl.github.io/trcks/)
- [OOP usage guide](https://christophgietl.github.io/trcks/usage/oop/)
- [FP usage guide](https://christophgietl.github.io/trcks/usage/fp/)
- [OOP and FP equivalence table](https://christophgietl.github.io/trcks/usage/oop-and-fp-equivalence/)
- [API reference](https://christophgietl.github.io/trcks/reference/trcks/)
- [Glossary](https://christophgietl.github.io/trcks/glossary/)
- [Motivation for railway-oriented programming](https://christophgietl.github.io/trcks/motivation/railway-oriented-programming/)
