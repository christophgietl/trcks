# `trcks.oop` and `trcks.fp` equivalence

`trcks` supports two equivalent programming styles:
[trcks.oop][] (method chaining)
and [trcks.fp][] (function composition).
This page maps common operations from one style to the other.

| Operation | `trcks.oop` | `trcks.fp` |
|---|---|---|
| Wrap a value | [`Wrapper(core=x)`][trcks.oop.Wrapper] | start value of a `pipe(...)` call |
| Map a plain value | [`.map(f)`][trcks.oop.Wrapper.map] | [`pipe((x, f))`][trcks.fp.composition.pipe] |
| Map success to `Result` | [`.map_success_to_result(f)`][trcks.oop.ResultWrapper.map_success_to_result] | [`r.map_success_to_result(f)`][trcks.fp.monads.result.map_success_to_result] |
| Map on success | [`.map_success(f)`][trcks.oop.ResultWrapper.map_success] | [`r.map_success(f)`][trcks.fp.monads.result.map_success] |
| Map on failure | [`.map_failure(f)`][trcks.oop.ResultWrapper.map_failure] | [`r.map_failure(f)`][trcks.fp.monads.result.map_failure] |
| Side effect on success | [`.tap_success(f)`][trcks.oop.ResultWrapper.tap_success] | [`r.tap_success(f)`][trcks.fp.monads.result.tap_success] |
| Failable side effect on success | [`.tap_success_to_result(f)`][trcks.oop.ResultWrapper.tap_success_to_result] | [`r.tap_success_to_result(f)`][trcks.fp.monads.result.tap_success_to_result] |
| Async success step | [`.map_success_to_awaitable_result(f)`][trcks.oop.ResultWrapper.map_success_to_awaitable_result] | [`r.map_success_to_awaitable_result(f)`][trcks.fp.monads.result.map_success_to_awaitable_result] |
| Unwrap the result | `.core` | result of `pipe(...)` |

## Widening `Result` into richer monads

`ResultWrapper` also has methods that transition into a richer wrapper
(e.g. `AwaitableResultWrapper`, `ResultTupleWrapper`,
`AwaitableResultTupleWrapper`).
[`trcks.fp.monads.result`][] mirrors every one of these methods
under the same name,
so the [`trcks.oop`](oop/index.md) and [`trcks.fp`](fp/index.md) styles stay
call-compatible for widening operations too.

| `trcks.oop` (`ResultWrapper` method) | `trcks.fp` (`trcks.fp.monads.result` function) |
|---|---|
| [`.map_failure_to_awaitable(f)`][trcks.oop.ResultWrapper.map_failure_to_awaitable] | [`r.map_failure_to_awaitable(f)`][trcks.fp.monads.result.map_failure_to_awaitable] |
| [`.map_failure_to_awaitable_result(f)`][trcks.oop.ResultWrapper.map_failure_to_awaitable_result] | [`r.map_failure_to_awaitable_result(f)`][trcks.fp.monads.result.map_failure_to_awaitable_result] |
| [`.map_failure_to_awaitable_result_iterable(f)`][trcks.oop.ResultWrapper.map_failure_to_awaitable_result_iterable] | [`r.map_failure_to_awaitable_result_iterable(f)`][trcks.fp.monads.result.map_failure_to_awaitable_result_iterable] |
| [`.map_failure_to_iterable(f)`][trcks.oop.ResultWrapper.map_failure_to_iterable] | [`r.map_failure_to_iterable(f)`][trcks.fp.monads.result.map_failure_to_iterable] |
| [`.map_failure_to_result_iterable(f)`][trcks.oop.ResultWrapper.map_failure_to_result_iterable] | [`r.map_failure_to_result_iterable(f)`][trcks.fp.monads.result.map_failure_to_result_iterable] |
| [`.map_success_to_awaitable(f)`][trcks.oop.ResultWrapper.map_success_to_awaitable] | [`r.map_success_to_awaitable(f)`][trcks.fp.monads.result.map_success_to_awaitable] |
| [`.map_success_to_awaitable_result(f)`][trcks.oop.ResultWrapper.map_success_to_awaitable_result] | [`r.map_success_to_awaitable_result(f)`][trcks.fp.monads.result.map_success_to_awaitable_result] |
| [`.map_success_to_awaitable_result_iterable(f)`][trcks.oop.ResultWrapper.map_success_to_awaitable_result_iterable] | [`r.map_success_to_awaitable_result_iterable(f)`][trcks.fp.monads.result.map_success_to_awaitable_result_iterable] |
| [`.map_success_to_iterable(f)`][trcks.oop.ResultWrapper.map_success_to_iterable] | [`r.map_success_to_iterable(f)`][trcks.fp.monads.result.map_success_to_iterable] |
| [`.map_success_to_result_iterable(f)`][trcks.oop.ResultWrapper.map_success_to_result_iterable] | [`r.map_success_to_result_iterable(f)`][trcks.fp.monads.result.map_success_to_result_iterable] |
| [`.tap_failure_to_awaitable(f)`][trcks.oop.ResultWrapper.tap_failure_to_awaitable] | [`r.tap_failure_to_awaitable(f)`][trcks.fp.monads.result.tap_failure_to_awaitable] |
| [`.tap_failure_to_awaitable_result(f)`][trcks.oop.ResultWrapper.tap_failure_to_awaitable_result] | [`r.tap_failure_to_awaitable_result(f)`][trcks.fp.monads.result.tap_failure_to_awaitable_result] |
| [`.tap_failure_to_awaitable_result_iterable(f)`][trcks.oop.ResultWrapper.tap_failure_to_awaitable_result_iterable] | [`r.tap_failure_to_awaitable_result_iterable(f)`][trcks.fp.monads.result.tap_failure_to_awaitable_result_iterable] |
| [`.tap_failure_to_iterable(f)`][trcks.oop.ResultWrapper.tap_failure_to_iterable] | [`r.tap_failure_to_iterable(f)`][trcks.fp.monads.result.tap_failure_to_iterable] |
| [`.tap_failure_to_result_iterable(f)`][trcks.oop.ResultWrapper.tap_failure_to_result_iterable] | [`r.tap_failure_to_result_iterable(f)`][trcks.fp.monads.result.tap_failure_to_result_iterable] |
| [`.tap_success_to_awaitable(f)`][trcks.oop.ResultWrapper.tap_success_to_awaitable] | [`r.tap_success_to_awaitable(f)`][trcks.fp.monads.result.tap_success_to_awaitable] |
| [`.tap_success_to_awaitable_result(f)`][trcks.oop.ResultWrapper.tap_success_to_awaitable_result] | [`r.tap_success_to_awaitable_result(f)`][trcks.fp.monads.result.tap_success_to_awaitable_result] |
| [`.tap_success_to_awaitable_result_iterable(f)`][trcks.oop.ResultWrapper.tap_success_to_awaitable_result_iterable] | [`r.tap_success_to_awaitable_result_iterable(f)`][trcks.fp.monads.result.tap_success_to_awaitable_result_iterable] |
| [`.tap_success_to_iterable(f)`][trcks.oop.ResultWrapper.tap_success_to_iterable] | [`r.tap_success_to_iterable(f)`][trcks.fp.monads.result.tap_success_to_iterable] |
| [`.tap_success_to_result_iterable(f)`][trcks.oop.ResultWrapper.tap_success_to_result_iterable] | [`r.tap_success_to_result_iterable(f)`][trcks.fp.monads.result.tap_success_to_result_iterable] |

## Widening homogeneous tuples into richer monads

`TupleWrapper` also has methods that transition into a richer wrapper
(e.g. `AwaitableTupleWrapper`, `ResultTupleWrapper`,
`AwaitableResultTupleWrapper`).
[`trcks.fp.monads.tuple_`][] mirrors every one of these methods
under the same name,
so the [`trcks.oop`](oop/index.md) and [`trcks.fp`](fp/index.md) styles stay
call-compatible for widening operations too.

| `trcks.oop` (`TupleWrapper` method) | `trcks.fp` (`trcks.fp.monads.tuple_` function) |
|---|---|
| [`.map_to_awaitable(f)`][trcks.oop.TupleWrapper.map_to_awaitable] | [`t.map_to_awaitable(f)`][trcks.fp.monads.tuple_.map_to_awaitable] |
| [`.map_to_awaitable_iterable(f)`][trcks.oop.TupleWrapper.map_to_awaitable_iterable] | [`t.map_to_awaitable_iterable(f)`][trcks.fp.monads.tuple_.map_to_awaitable_iterable] |
| [`.map_to_awaitable_result(f)`][trcks.oop.TupleWrapper.map_to_awaitable_result] | [`t.map_to_awaitable_result(f)`][trcks.fp.monads.tuple_.map_to_awaitable_result] |
| [`.map_to_awaitable_result_iterable(f)`][trcks.oop.TupleWrapper.map_to_awaitable_result_iterable] | [`t.map_to_awaitable_result_iterable(f)`][trcks.fp.monads.tuple_.map_to_awaitable_result_iterable] |
| [`.map_to_result(f)`][trcks.oop.TupleWrapper.map_to_result] | [`t.map_to_result(f)`][trcks.fp.monads.tuple_.map_to_result] |
| [`.map_to_result_iterable(f)`][trcks.oop.TupleWrapper.map_to_result_iterable] | [`t.map_to_result_iterable(f)`][trcks.fp.monads.tuple_.map_to_result_iterable] |
| [`.tap_to_awaitable(f)`][trcks.oop.TupleWrapper.tap_to_awaitable] | [`t.tap_to_awaitable(f)`][trcks.fp.monads.tuple_.tap_to_awaitable] |
| [`.tap_to_awaitable_iterable(f)`][trcks.oop.TupleWrapper.tap_to_awaitable_iterable] | [`t.tap_to_awaitable_iterable(f)`][trcks.fp.monads.tuple_.tap_to_awaitable_iterable] |
| [`.tap_to_awaitable_result(f)`][trcks.oop.TupleWrapper.tap_to_awaitable_result] | [`t.tap_to_awaitable_result(f)`][trcks.fp.monads.tuple_.tap_to_awaitable_result] |
| [`.tap_to_awaitable_result_iterable(f)`][trcks.oop.TupleWrapper.tap_to_awaitable_result_iterable] | [`t.tap_to_awaitable_result_iterable(f)`][trcks.fp.monads.tuple_.tap_to_awaitable_result_iterable] |
| [`.tap_to_result(f)`][trcks.oop.TupleWrapper.tap_to_result] | [`t.tap_to_result(f)`][trcks.fp.monads.tuple_.tap_to_result] |
| [`.tap_to_result_iterable(f)`][trcks.oop.TupleWrapper.tap_to_result_iterable] | [`t.tap_to_result_iterable(f)`][trcks.fp.monads.tuple_.tap_to_result_iterable] |

## Widening awaitables into richer monads

`AwaitableWrapper` also has methods that transition into a richer wrapper
(e.g. `AwaitableTupleWrapper`, `AwaitableResultWrapper`,
`AwaitableResultTupleWrapper`).
[`trcks.fp.monads.awaitable`][] mirrors every one of these methods
under the same name,
so the [`trcks.oop`](oop/index.md) and [`trcks.fp`](fp/index.md) styles stay
call-compatible for widening operations too.

| `trcks.oop` (`AwaitableWrapper` method) | `trcks.fp` (`trcks.fp.monads.awaitable` function) |
|---|---|
| [`.map_to_awaitable_iterable(f)`][trcks.oop.AwaitableWrapper.map_to_awaitable_iterable] | [`a.map_to_awaitable_iterable(f)`][trcks.fp.monads.awaitable.map_to_awaitable_iterable] |
| [`.map_to_awaitable_result(f)`][trcks.oop.AwaitableWrapper.map_to_awaitable_result] | [`a.map_to_awaitable_result(f)`][trcks.fp.monads.awaitable.map_to_awaitable_result] |
| [`.map_to_awaitable_result_iterable(f)`][trcks.oop.AwaitableWrapper.map_to_awaitable_result_iterable] | [`a.map_to_awaitable_result_iterable(f)`][trcks.fp.monads.awaitable.map_to_awaitable_result_iterable] |
| [`.map_to_iterable(f)`][trcks.oop.AwaitableWrapper.map_to_iterable] | [`a.map_to_iterable(f)`][trcks.fp.monads.awaitable.map_to_iterable] |
| [`.map_to_result(f)`][trcks.oop.AwaitableWrapper.map_to_result] | [`a.map_to_result(f)`][trcks.fp.monads.awaitable.map_to_result] |
| [`.map_to_result_iterable(f)`][trcks.oop.AwaitableWrapper.map_to_result_iterable] | [`a.map_to_result_iterable(f)`][trcks.fp.monads.awaitable.map_to_result_iterable] |
| [`.tap_to_awaitable_iterable(f)`][trcks.oop.AwaitableWrapper.tap_to_awaitable_iterable] | [`a.tap_to_awaitable_iterable(f)`][trcks.fp.monads.awaitable.tap_to_awaitable_iterable] |
| [`.tap_to_awaitable_result(f)`][trcks.oop.AwaitableWrapper.tap_to_awaitable_result] | [`a.tap_to_awaitable_result(f)`][trcks.fp.monads.awaitable.tap_to_awaitable_result] |
| [`.tap_to_awaitable_result_iterable(f)`][trcks.oop.AwaitableWrapper.tap_to_awaitable_result_iterable] | [`a.tap_to_awaitable_result_iterable(f)`][trcks.fp.monads.awaitable.tap_to_awaitable_result_iterable] |
| [`.tap_to_iterable(f)`][trcks.oop.AwaitableWrapper.tap_to_iterable] | [`a.tap_to_iterable(f)`][trcks.fp.monads.awaitable.tap_to_iterable] |
| [`.tap_to_result(f)`][trcks.oop.AwaitableWrapper.tap_to_result] | [`a.tap_to_result(f)`][trcks.fp.monads.awaitable.tap_to_result] |
| [`.tap_to_result_iterable(f)`][trcks.oop.AwaitableWrapper.tap_to_result_iterable] | [`a.tap_to_result_iterable(f)`][trcks.fp.monads.awaitable.tap_to_result_iterable] |

## Widening plain values into richer monads

`Wrapper` also has methods that transition into a richer wrapper
(e.g. `AwaitableWrapper`, `ResultWrapper`, `TupleWrapper`).
[`trcks.fp.monads.identity`][] mirrors every one of these methods
under the same name,
so the [`trcks.oop`](oop/index.md) and [`trcks.fp`](fp/index.md) styles stay
call-compatible for widening operations too.

| `trcks.oop` (`Wrapper` method) | `trcks.fp` (`trcks.fp.monads.identity` function) |
|---|---|
| [`.map_to_awaitable(f)`][trcks.oop.Wrapper.map_to_awaitable] | [`i.map_to_awaitable(f)`][trcks.fp.monads.identity.map_to_awaitable] |
| [`.map_to_awaitable_iterable(f)`][trcks.oop.Wrapper.map_to_awaitable_iterable] | [`i.map_to_awaitable_iterable(f)`][trcks.fp.monads.identity.map_to_awaitable_iterable] |
| [`.map_to_awaitable_result(f)`][trcks.oop.Wrapper.map_to_awaitable_result] | [`i.map_to_awaitable_result(f)`][trcks.fp.monads.identity.map_to_awaitable_result] |
| [`.map_to_awaitable_result_iterable(f)`][trcks.oop.Wrapper.map_to_awaitable_result_iterable] | [`i.map_to_awaitable_result_iterable(f)`][trcks.fp.monads.identity.map_to_awaitable_result_iterable] |
| [`.map_to_iterable(f)`][trcks.oop.Wrapper.map_to_iterable] | [`i.map_to_iterable(f)`][trcks.fp.monads.identity.map_to_iterable] |
| [`.map_to_result(f)`][trcks.oop.Wrapper.map_to_result] | [`i.map_to_result(f)`][trcks.fp.monads.identity.map_to_result] |
| [`.map_to_result_iterable(f)`][trcks.oop.Wrapper.map_to_result_iterable] | [`i.map_to_result_iterable(f)`][trcks.fp.monads.identity.map_to_result_iterable] |
| [`.tap_to_awaitable(f)`][trcks.oop.Wrapper.tap_to_awaitable] | [`i.tap_to_awaitable(f)`][trcks.fp.monads.identity.tap_to_awaitable] |
| [`.tap_to_awaitable_iterable(f)`][trcks.oop.Wrapper.tap_to_awaitable_iterable] | [`i.tap_to_awaitable_iterable(f)`][trcks.fp.monads.identity.tap_to_awaitable_iterable] |
| [`.tap_to_awaitable_result(f)`][trcks.oop.Wrapper.tap_to_awaitable_result] | [`i.tap_to_awaitable_result(f)`][trcks.fp.monads.identity.tap_to_awaitable_result] |
| [`.tap_to_awaitable_result_iterable(f)`][trcks.oop.Wrapper.tap_to_awaitable_result_iterable] | [`i.tap_to_awaitable_result_iterable(f)`][trcks.fp.monads.identity.tap_to_awaitable_result_iterable] |
| [`.tap_to_iterable(f)`][trcks.oop.Wrapper.tap_to_iterable] | [`i.tap_to_iterable(f)`][trcks.fp.monads.identity.tap_to_iterable] |
| [`.tap_to_result(f)`][trcks.oop.Wrapper.tap_to_result] | [`i.tap_to_result(f)`][trcks.fp.monads.identity.tap_to_result] |
| [`.tap_to_result_iterable(f)`][trcks.oop.Wrapper.tap_to_result_iterable] | [`i.tap_to_result_iterable(f)`][trcks.fp.monads.identity.tap_to_result_iterable] |

`trcks.fp.monads.awaitable`, `trcks.fp.monads.identity`,
`trcks.fp.monads.result`, and
`trcks.fp.monads.tuple_` implement these by
lifting the value into the richer monad
(e.g. via [`trcks.fp.monads.awaitable_result.construct_success_from_awaitable`][],
[`trcks.fp.monads.result.construct_success`][],
[`trcks.fp.monads.awaitable_result.construct_from_result`][], and
[`trcks.fp.monads.awaitable_tuple.construct_from_iterable`][])
and then applying that monad's own function.
This lift-then-apply composition is available as a general pattern via
[`trcks.fp.composition.pipe`][],
but only widening operations for the `Awaitable` monad,
for the `Result` monad,
for homogeneous tuples, and
for plain values have a dedicated function so far.
Widenings for the other monads still require an explicit
`pipe((..., construct_from_result, ...))` step.

The full set of element-wise and homogeneous-tuple variants is covered
in the
[`trcks.oop` usage pages](oop/index.md),
the
[`trcks.fp` usage pages](fp/index.md),
and the [Reference](../reference/trcks.oop.md) section.
