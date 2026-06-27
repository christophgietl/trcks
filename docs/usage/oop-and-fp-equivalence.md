# OOP and FP equivalence

`trcks` supports two equivalent programming styles:
an object-oriented (OOP) style based on method chaining
([trcks.oop][])
and a functional (FP) style based on function composition
([trcks.fp][]).
This page maps common operations from one style to the other.

<!-- rumdl-disable MD013 -->

| Operation | OOP (`trcks.oop`) | FP (`trcks.fp`) |
|---|---|---|
| Wrap a value | [`Wrapper(core=x)`][trcks.oop.Wrapper] | start value of a `pipe(...)` call |
| Map a plain value | [`.map(f)`][trcks.oop.Wrapper.map] | [`pipe((x, f))`][trcks.fp.composition.pipe] |
| Map on success | [`.map_success(f)`][trcks.oop.ResultWrapper.map_success] | [`r.map_success(f)`][trcks.fp.monads.result.map_success] |
| Map success to `Result` | [`.map_success_to_result(f)`][trcks.oop.ResultWrapper.map_success_to_result] | [`r.map_success_to_result(f)`][trcks.fp.monads.result.map_success_to_result] |
| Map on failure | [`.map_failure(f)`][trcks.oop.ResultWrapper.map_failure] | [`r.map_failure(f)`][trcks.fp.monads.result.map_failure] |
| Side effect on success | [`.tap_success(f)`][trcks.oop.ResultWrapper.tap_success] | [`r.tap_success(f)`][trcks.fp.monads.result.tap_success] |
| Failable side effect on success | [`.tap_success_to_result(f)`][trcks.oop.ResultWrapper.tap_success_to_result] | [`r.tap_success_to_result(f)`][trcks.fp.monads.result.tap_success_to_result] |
| Async success step | [`.map_success_to_awaitable_result(f)`][trcks.oop.ResultWrapper.map_success_to_awaitable_result] | [`ar.map_success_to_awaitable_result(f)`][trcks.fp.monads.awaitable_result.map_success_to_awaitable_result] |
| Unwrap the result | `.core` (or `.core_as_coroutine` for async) | result of `pipe(...)` (or [`ar.to_coroutine_result(...)`][trcks.fp.monads.awaitable_result.to_coroutine_result] for async) |

The full set of element-wise and homogeneous-tuple variants is covered
in the
[OOP usage page](railway-oriented-programming-with-trcks-oop.md),
the
[FP usage page](railway-oriented-programming-with-trcks-fp.md),
and the [Reference](../reference/trcks.oop.md) section.

<!-- rumdl-enable MD013 -->
