# Glossary

This page collects the key terms used across the `trcks` documentation.

## `Awaitable` and `Coroutine`

`collections.abc.Awaitable[T]` is the broad type for anything
that can be `await`-ed; `collections.abc.Coroutine` is a specific,
narrower subtype produced by `async def` functions.
`asyncio.run` requires a `Coroutine`, not just any `Awaitable`,
which is why `trcks` provides helpers such as
`core_as_coroutine` ([trcks.oop][]) and `ar.to_coroutine_result`
([trcks.fp][]) to convert an `Awaitable` result into a `Coroutine`.

## Double-track

A value that is either a success or a failure, represented by
[trcks.Result][].
One track carries successful results forward;
the other carries failure descriptions.

## Higher-order function

A function that accepts a function as an argument,
returns a function, or both.
The `map_*` helpers in `trcks` are higher-order functions.

## Homogeneous tuple

A `tuple[T, ...]` whose every element shares the same type and
is processed element-wise.
`trcks` wraps homogeneous tuples so that each element can be mapped
or validated independently.

## Mapping helper (or `map_*` function)

A helper that lifts a plain function so that it operates on a
wrapped value ([trcks.oop][]) or becomes a pipeline step ([trcks.fp][]).
For example, `.map_success` on a
[trcks.oop.ResultWrapper][] and `r.map_success` from
[trcks.fp.monads.result][] both apply a function to the success
value of a [trcks.Result][], leaving failures unchanged.
The modules under `trcks.fp.monads` are where these helpers live.

## Pipeline and `pipe`

A pipeline is a tuple consisting of a start value followed by a
sequence of compatible functions.
[trcks.fp.composition.pipe][] runs the pipeline by passing the
start value through each function in turn.

## Railway-oriented programming (ROP)

A design pattern for composing functions that may fail.
See the [motivation page](motivation/railway-oriented-programming.md)
for a full introduction.

## Short-circuiting

Once a step produces a failure, all subsequent `map_success*` steps
are skipped and the failure is carried through to the end of the
pipeline without further processing.

## Single-track

A value that is either always present or always absent —
in other words, an ordinary Python value with no success-or-failure
wrapper.

## Success, Failure, and Result

The three generic types at the heart of `trcks`.
See [Tuple types provided by trcks](usage/tuple-types-provided-by-trcks.md)
for definitions and examples.

## `tap` and side effects

A side effect is an operation (such as logging or file I/O) that does
not change the value flowing through the pipeline.
The `tap_*` helpers run a side effect and then return the original
value unchanged, keeping the pipeline intact.
