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
| Async success step | [`.map_success_to_awaitable_result(f)`][trcks.oop.ResultWrapper.map_success_to_awaitable_result] | [`ar.map_success_to_awaitable_result(f)`][trcks.fp.monads.awaitable_result.map_success_to_awaitable_result] |
| Unwrap the result | `.core` | result of `pipe(...)` |

The full set of element-wise and homogeneous-tuple variants is covered
in the
[`trcks.oop` usage page](railway-oriented-programming-with-trcks-oop.md),
the
[`trcks.fp` usage page](railway-oriented-programming-with-trcks-fp.md),
and the [Reference](../reference/trcks.oop.md) section.
