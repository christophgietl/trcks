# Glossary

This page collects the key terms used across the `trcks` documentation.

## `Awaitable` and `Coroutine`

[collections.abc.Awaitable][] is the broad type for anything
that can be awaited using `await`.
[collections.abc.Coroutine][] is a specific, narrower subtype
produced by `async def` functions.
In Python 3.13 and older, [asyncio.run][] requires a `Coroutine`, not just any `Awaitable`.
`trcks` provides helpers such as
[trcks.oop.BaseAwaitableWrapper.core_as_coroutine][] and
[trcks.fp.monads.awaitable_result.to_coroutine_result][] to convert an `Awaitable`
result into a `Coroutine`.

## Double-track

A value that is either a success or a failure, represented by
[trcks.Result][].
One track carries successful results forward;
the other carries information about failures.

## Higher-order function

A function that accepts a function as an argument,
returns a function, or both.
The `map_*` helpers in `trcks` are higher-order functions.

## Homogeneous tuple

A `tuple[T, ...]` whose elements all share the same type,
processed individually by `trcks`.

## Mapping helper (or `map_*` function)

A helper that lifts a plain function so that it operates on a
wrapped value ([trcks.oop][]) or becomes a pipeline step ([trcks.fp][]).
For example, [trcks.oop.ResultWrapper.map_success][] and
[trcks.fp.monads.result.map_success][] both apply a function to the success
value of a [trcks.Result][], leaving failures unchanged.
These helpers live in `trcks.oop` classes and in the modules under `trcks.fp.monads`.

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

Once a step produces a failure, all subsequent `map_*` steps
are skipped and the failure is carried through to the end of the
pipeline without further processing.

## Single-track

A plain Python value not wrapped in a success-or-failure type —
in other words, an ordinary Python value that carries no information
about whether an operation succeeded or failed.

## Success, Failure, and Result

The three generic types at the heart of `trcks`.
See [Tuple types provided by trcks](usage/tuple-types-provided-by-trcks.md)
for definitions and examples.

## `tap` and side effects

A side effect is an operation (such as logging or file I/O) that does
not change the value flowing through the pipeline.
The `tap_*` helpers run a side effect and then return the original
value unchanged, keeping the pipeline intact.
