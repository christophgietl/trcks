# Railway-oriented programming with [trcks.fp][]

Railway-oriented programming (ROP) is a pattern for composing functions
that may fail, keeping error handling clean and explicit.
This page covers the **functional style**: you build a pipeline as a
tuple of a start value and a sequence of functions, then run it with
[trcks.fp.composition.pipe][] — a "build a pipeline, then run it"
mental model.
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
      for a side-by-side comparison with the object-oriented style.

## Overview matrix

| Runtime and track | Single value | Homogeneous tuple |
|---|---|---|
| Sync and single-track | [`pipe` and `identity`](sync.md#single-track-code-with-trcksfpcomposition) | [`tuple_`](tuples.md#synchronous-single-track-code-with-trcksfpmonadstuple_) |
| Sync and double-track | [`result`](sync.md#double-track-code-with-trcksfpmonadsresult) | [`result_tuple`](tuples.md#synchronous-double-track-code-with-trcksfpmonadsresult_tuple) |
| Async and single-track | [`awaitable`](async.md#single-track-code-with-trcksfpmonadsawaitable) | [`awaitable_tuple`](tuples.md#asynchronous-single-track-code-with-trcksfpmonadsawaitable_tuple) |
| Async and double-track | [`awaitable_result`](async.md#double-track-code-with-trcksfpmonadsawaitable_result) | [`awaitable_result_tuple`](tuples.md#asynchronous-double-track-code-with-trcksfpmonadsawaitable_result_tuple) |

???+ tip "See also"
    The [OOP usage page](../oop/index.md)
    covers the same operations using method chaining instead of
    function composition.
