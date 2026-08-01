# Railway-oriented programming with [trcks.oop][]

Railway-oriented programming (ROP) is a pattern for composing functions
that may fail, keeping error handling clean and explicit.
This page covers the **object-oriented style**: you wrap a value in a
[trcks.oop.Wrapper][] subclass, chain method calls to transform it, and
then unwrap the result — a "wrap → map → unwrap" mental model.
Single-track and double-track code are both discussed.
Synchronous and asynchronous code are also discussed.

???+ note "Prerequisites"
    - Read
      [Tuple types provided by trcks](../tuple-types-provided-by-trcks.md)
      first; this page assumes familiarity with
      [trcks.Failure][], [trcks.Success][], and [trcks.Result][].
    - The
      [motivation page for ROP](../../motivation/railway-oriented-programming.md)
      explains the design rationale.
    - The async sections assume comfort with `async`, `await`, and
      `asyncio.run`.
    - See the [glossary](../../glossary.md) for definitions of terms such
      as "single-track", "double-track", and "short-circuiting".
    - See the
      [OOP and FP equivalence table](../oop-and-fp-equivalence.md)
      for a side-by-side comparison with the functional style.

## Overview matrix

| Runtime and track | Single value | Homogeneous tuple |
|---|---|---|
| Sync and single-track | [`Wrapper`](sync.md#single-track-code-with-trcksoopwrapper) | [`TupleWrapper`](tuples.md#synchronous-single-track-code-with-trcksooptuplewrapper) |
| Sync and double-track | [`ResultWrapper`](sync.md#double-track-code-with-trcksoopresultwrapper) | [`ResultTupleWrapper`](tuples.md#synchronous-double-track-code-with-trcksoopresulttuplewrapper) |
| Async and single-track | [`AwaitableWrapper`](async.md#single-track-code-with-trcksoopawaitablewrapper) | [`AwaitableTupleWrapper`](tuples.md#asynchronous-single-track-code-with-trcksoopawaitabletuplewrapper) |
| Async and double-track | [`AwaitableResultWrapper`](async.md#double-track-code-with-trcksoopawaitableresultwrapper) | [`AwaitableResultTupleWrapper`](tuples.md#asynchronous-double-track-code-with-trcksoopawaitableresulttuplewrapper) |

???+ tip "See also"
    The [FP usage page](../fp/index.md)
    covers the same operations using function composition instead of
    method chaining.
