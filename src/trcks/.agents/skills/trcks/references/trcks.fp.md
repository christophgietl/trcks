# Railway-oriented programming (ROP) with `trcks.fp`

The subpackage `trcks.fp` provides functions and higher-order functions
for railway-oriented programming (ROP) in a functional programming style
based on function composition.

## Composing functions with `trcks.fp.composition`

A `Pipeline` is a tuple consisting of a start value followed by up to
seven compatible functions.
Use `trcks.fp.composition.pipe` to evaluate a `Pipeline`,
applying the functions sequentially from first to last:

```pycon
>>> from trcks.fp.composition import pipe
>>> def to_length_string(s: str) -> str:
...     return pipe((s, len, lambda n: f"Length: {n}"))
...
>>> to_length_string("Hello, world!")
'Length: 13'

```

The type aliases `Pipeline0`, `Pipeline1`, ..., `Pipeline7` describe
`Pipeline` tuples of a fixed length,
and the type alias `Pipeline` combines all of them.
If your static type checker cannot infer the type of a `Pipeline`,
assign one of these type aliases to the tuple explicitly:

```pycon
>>> from trcks.fp.composition import Pipeline0, Pipeline1, Pipeline2
>>> p0: Pipeline0[str] = ("Hello, world!",)
>>> pipe(p0)
'Hello, world!'
>>> p1: Pipeline1[str, int] = ("Hello, world!", len)
>>> pipe(p1)
13
>>> p2: Pipeline2[str, int, str] = (
...     "Hello, world!",
...     len,
...     lambda n: f"Length: {n}",
... )
>>> pipe(p2)
'Length: 13'

```

## Synchronous ROP with `trcks.fp`

### Modules for processing plain values, `trcks.Result` values, homogeneous tuples, and `trcks.ResultTuple` values

The module `trcks.fp.monads.identity` provides a single higher-order
function for plain values.
The module `trcks.fp.monads.result` provides higher-order functions
for `trcks.Result` values.
The module `trcks.fp.monads.tuple_` provides higher-order functions
for homogeneous tuples.
The module `trcks.fp.monads.result_tuple` provides higher-order functions
for `trcks.ResultTuple` values.
By convention, these modules are imported under short aliases:

```pycon
>>> from trcks.fp.monads import (
...     identity as i,
...     result as r,
...     result_tuple as rt,
...     tuple_ as t,
... )

```

Each module follows shared naming conventions.
Functions named `construct*` build a wrapped value from plain values or
from "complex" values.
Functions named `map*` transform a wrapped value, and functions named
`tap*` apply a side effect to a wrapped value without changing it.
For `trcks.Result` and `trcks.ResultTuple` values,
the suffix `_failure` selects functions that operate on the failure track,
and the suffixes `_success` and `_successes` select functions that operate
on the success track.

### Constructing `trcks.Result` values, tuples, and `trcks.ResultTuple` values from plain values

Use `result.construct_failure` or `result.construct_success`
to construct a `trcks.Result` object from a plain value:

```pycon
>>> r.construct_failure("Error")
('failure', 'Error')
>>> r.construct_success(42)
('success', 42)

```

Use `tuple_.construct` to construct a 1-element tuple from a plain value:

```pycon
>>> t.construct(42)
(42,)

```

Use `result_tuple.construct_failure` or `result_tuple.construct_successes`
to construct a `trcks.ResultTuple` object from a plain value:

```pycon
>>> rt.construct_failure("not found")
('failure', 'not found')
>>> rt.construct_successes(42)
('success', (42,))

```

### Constructing homogeneous tuples and `trcks.ResultTuple` values from "complex" values

Use the built-in `tuple` constructor to build a homogeneous tuple
from a `collections.abc.Iterable`:

```pycon
>>> tuple([1, 2, 3])
(1, 2, 3)

```

Use `result_tuple.construct_from_result` or
`result_tuple.construct_from_result_iterable`
to construct a `trcks.ResultTuple` from a `trcks.Result` or
a `trcks.ResultIterable`:

```pycon
>>> rt.construct_from_result(("success", 7))
('success', (7,))
>>> rt.construct_from_result_iterable(("success", [1, 2]))
('success', (1, 2))

```

Use `result_tuple.construct_successes_from_iterable`
to construct a `trcks.SuccessTuple` from a `collections.abc.Iterable`:

```pycon
>>> rt.construct_successes_from_iterable((1, 2))
('success', (1, 2))

```

### Mapping inner values to plain values

Use `tuple_.map_` to apply a function to each element of a homogeneous
tuple:

```pycon
>>> t.map_(len)(("a", "bb", "ccc"))
(1, 2, 3)

```

Use `result.map_failure` and `result.map_success`
to apply functions to the failure or success value of a `trcks.Result`:

```pycon
>>> r.map_failure(lambda s: f"Prefix: {s}")(("failure", "negative value"))
('failure', 'Prefix: negative value')
>>> r.map_success(lambda n: n + 1)(("success", 42))
('success', 43)

```

Use `result_tuple.map_failure` and `result_tuple.map_successes`
to apply functions to the failure value or to each success element
of a `trcks.ResultTuple`:

```pycon
>>> rt.map_failure(lambda s: f"err: {s}")(("failure", "not found"))
('failure', 'err: not found')
>>> rt.map_successes(lambda n: n * 2)(("success", (1, 2, 3)))
('success', (2, 4, 6))

```

### Mapping inner values to "complex" values

Use `tuple_.map_to_iterable` to apply a function returning a
`collections.abc.Iterable` to each element of a homogeneous tuple,
flattening the result:

```pycon
>>> def duplicate(n: int) -> tuple[int, int]:
...     return n, n
...
>>> t.map_to_iterable(duplicate)((1, 2, 3))
(1, 1, 2, 2, 3, 3)

```

Use `result.map_failure_to_result` and `result.map_success_to_result`
to apply functions with return type `trcks.Result`
to the failure or success value of a `trcks.Result`:

```pycon
>>> from trcks import Result
>>> def replace_not_found_by_default_value(s: str) -> Result[str, float]:
...     if s == "not found":
...         return "success", 0.0
...     return "failure", s
...
>>> r.map_failure_to_result(replace_not_found_by_default_value)(
...     ("failure", "not found")
... )
('success', 0.0)
>>> def get_square_root(x: float) -> Result[str, float]:
...     if x < 0:
...         return "failure", "negative value"
...     return "success", x**0.5
...
>>> r.map_success_to_result(get_square_root)(("success", 25.0))
('success', 5.0)

```

Use `result_tuple.map_failure_to_result` and
`result_tuple.map_successes_to_result`
to apply functions with return type `trcks.Result`
to the failure value or to each success element of a `trcks.ResultTuple`:

```pycon
>>> def double_if_positive(n: int) -> Result[str, int]:
...     if n > 0:
...         return "success", n * 2
...     return "failure", "not positive"
...
>>> rt.map_successes_to_result(double_if_positive)(("success", (1, 2, 3)))
('success', (2, 4, 6))
>>> rt.map_successes_to_result(double_if_positive)(("success", (1, -1, 2)))
('failure', 'not positive')

```

Use `result_tuple.map_failure_to_iterable` and
`result_tuple.map_successes_to_iterable`
to apply functions returning a `collections.abc.Iterable`
to the failure value or to each success element of a `trcks.ResultTuple`,
flattening the result.
Use `result_tuple.map_successes_to_result_iterable`
to apply a function with return type `trcks.ResultIterable`
to each success element of a `trcks.ResultTuple`,
flattening the result and short-circuiting on the first failure:

```pycon
>>> from trcks import ResultTuple
>>> def duplicate_if_positive(n: int) -> ResultTuple[str, int]:
...     if n > 0:
...         return "success", (n, n)
...     return "failure", "not positive"
...
>>> rt.map_successes_to_result_iterable(duplicate_if_positive)(
...     ("success", (1, 2))
... )
('success', (1, 1, 2, 2))
>>> rt.map_successes_to_result_iterable(duplicate_if_positive)(
...     ("success", (1, -1, 2))
... )
('failure', 'not positive')

```

### Tapping inner values with plain side effects

Tapping applies a side effect (e.g. logging) to a wrapped value
without changing it.
Use `identity.tap` to apply a side effect to a plain value:

```pycon
>>> log_and_pass_on = i.tap(lambda o: print(f"Received object {o}."))
>>> output = log_and_pass_on(42)
Received object 42.
>>> output
42

```

Use `tuple_.tap` to apply a side effect to each element
of a homogeneous tuple:

```pycon
>>> def log_integer(n: int) -> None:
...     print(f"Received: {n}")
...
>>> t.tap(log_integer)((1, 2, 3))
Received: 1
Received: 2
Received: 3
(1, 2, 3)

```

Use `result.tap_failure` and `result.tap_success`
to apply side effects to the failure or success value of a `trcks.Result`:

```pycon
>>> log_failure = r.tap_failure(lambda s: print(f"Failure: {s}"))
>>> log_failure(("failure", "not found"))
Failure: not found
('failure', 'not found')
>>> log_failure(("success", 42))
('success', 42)
>>> log_success = r.tap_success(lambda n: print(f"Success: {n}"))
>>> log_success(("success", 42))
Success: 42
('success', 42)

```

Use `result_tuple.tap_failure` and `result_tuple.tap_successes`
to apply side effects to the failure value or to each success element
of a `trcks.ResultTuple`:

```pycon
>>> rt.tap_failure(lambda s: print(f"Error: {s}"))(("failure", "oops"))
Error: oops
('failure', 'oops')
>>> rt.tap_successes(log_integer)(("success", (1, 2)))
Received: 1
Received: 2
('success', (1, 2))

```

### Tapping inner values with "complex" side effects

The `tap*` functions shown above discard the return value of the side
effect.
`tap_failure_to_result`, `tap_success_to_result`, and
`tap_successes_to_result` functions apply a side effect with return type
`trcks.Result` instead.
For `tap_success_to_result` and `tap_successes_to_result`,
a returned `trcks.Failure` replaces the current value on the failure track,
while a returned `trcks.Success` leaves the tapped value unaffected.
`tap_failure_to_result` reverses these roles:
a returned `trcks.Success` replaces the current value on the success track,
while a returned `trcks.Failure` leaves the tapped value unaffected.
Similarly, `tap_to_iterable`, `tap_failure_to_iterable`, and
`tap_successes_to_iterable` functions apply a side effect returning a
`collections.abc.Iterable`, repeating the tapped value once per item
returned by the side effect.

Use `tuple_.tap_to_iterable` to repeat each element of a homogeneous
tuple once per item returned by the side effect:

```pycon
>>> def write_to_disk(n: int) -> tuple[str, str]:
...     print(f"Wrote {n} to disk.")
...     return "left", "right"
...
>>> t.tap_to_iterable(write_to_disk)((1, 2))
Wrote 1 to disk.
Wrote 2 to disk.
(1, 1, 2, 2)

```

Use `result.tap_failure_to_result` to apply a side effect
with return type `trcks.Result` to the failure value of a `trcks.Result`,
optionally recovering it into a success:

```pycon
>>> def replace_not_found_with_default(s: str) -> Result[object, float]:
...     if s == "not found":
...         return "success", 0.0
...     return "failure", s
...
>>> recover_from_not_found = r.tap_failure_to_result(
...     replace_not_found_with_default
... )
>>> recover_from_not_found(("failure", "not found"))
('success', 0.0)
>>> recover_from_not_found(("failure", "other error"))
('failure', 'other error')
>>> recover_from_not_found(("success", 42))
('success', 42)

```

Use `result.tap_success_to_result` to apply a side effect
with return type `trcks.Result` to the success value of a `trcks.Result`:

```pycon
>>> def persist(s: str) -> Result[str, object]:
...     if len(s) > 10:
...         return "failure", "out of disk space"
...     return "success", None
...
>>> persist_if_short = r.tap_success_to_result(persist)
>>> persist_if_short(("success", "short"))
('success', 'short')
>>> persist_if_short(("success", "a very long string"))
('failure', 'out of disk space')

```

Use `result_tuple.tap_successes_to_result` to apply a side effect
with return type `trcks.Result` to each success element of a
`trcks.ResultTuple`, letting any returned failure short-circuit the
tuple:

```pycon
>>> def validate_positive(n: int) -> Result[str, None]:
...     if n > 0:
...         return "success", None
...     return "failure", "not positive"
...
>>> validate_positive_successes = rt.tap_successes_to_result(
...     validate_positive
... )
>>> validate_positive_successes(("success", (1, 2)))
('success', (1, 2))
>>> validate_positive_successes(("success", (1, -1, 2)))
('failure', 'not positive')

```

## Asynchronous ROP with `trcks.fp`

### Modules for processing awaitable values, `trcks.AwaitableResult` values, awaitable tuples, and `trcks.AwaitableResultTuple` values

The module `trcks.fp.monads.awaitable` provides higher-order functions
for `collections.abc.Awaitable` values.
The module `trcks.fp.monads.awaitable_result` provides higher-order
functions for `trcks.AwaitableResult` values.
The module `trcks.fp.monads.awaitable_tuple` provides higher-order
functions for `trcks.AwaitableTuple` values.
The module `trcks.fp.monads.awaitable_result_tuple` provides higher-order
functions for `trcks.AwaitableResultTuple` values.
By convention, these modules are imported under short aliases:

```pycon
>>> from trcks.fp.monads import (
...     awaitable as a,
...     awaitable_result as ar,
...     awaitable_result_tuple as art,
...     awaitable_tuple as at,
... )

```

These modules share the same `construct*`, `map*`, and `tap*` naming
conventions introduced above.
Each `map*` and `tap*` function that also exists in the synchronous
modules gains an `_to_awaitable`, `_to_awaitable_iterable`,
`_to_awaitable_result`, or `_to_awaitable_result_iterable` counterpart
that applies an asynchronous, instead of a synchronous, function.
This section only covers what is specific to awaitable values.

### Constructing awaitable values, `trcks.AwaitableResult` values, awaitable tuples, and `trcks.AwaitableResultTuple` values

Use `awaitable.construct` to wrap a plain value
in an already resolved `collections.abc.Awaitable` object:

```pycon
>>> import asyncio
>>> asyncio.run(a.to_coroutine(a.construct(42)))
42

```

Use `awaitable_result.construct_success` or
`awaitable_result.construct_success_from_awaitable`
to construct a `trcks.AwaitableResult` from a value or from an awaitable
value:

```pycon
>>> async def read_from_disk() -> str:
...     await asyncio.sleep(0.001)
...     return "Hello, world!"
...
>>> a_rslt = ar.construct_success_from_awaitable(read_from_disk())
>>> asyncio.run(ar.to_coroutine_result(a_rslt))
('success', 'Hello, world!')

```

Use `awaitable_tuple.construct_from_iterable`
to construct a `trcks.AwaitableTuple` from a plain
`collections.abc.Iterable`:

```pycon
>>> a_tpl = at.construct_from_iterable([1, 2, 3])
>>> asyncio.run(at.to_coroutine_tuple(a_tpl))
(1, 2, 3)

```

Use `awaitable_result_tuple.construct_successes_from_iterable`
to construct a `trcks.AwaitableResultTuple` from a plain
`collections.abc.Iterable`:

```pycon
>>> a_r_tpl = art.construct_successes_from_iterable([1, 2])
>>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl))
('success', (1, 2))

```

### Entering the async track from a synchronous pipeline

If one of the functions in a `Pipeline` returns a
`collections.abc.Awaitable` value, the following function must accept
this `collections.abc.Awaitable` value as its input.
The higher-order functions in `trcks.fp.monads.awaitable` turn functions
expecting and returning plain values into functions expecting and
returning `collections.abc.Awaitable` values, allowing the pipeline to
continue on the async track:

```pycon
>>> from collections.abc import Awaitable
>>> from trcks.fp.composition import Pipeline3, pipe
>>> async def read_from_disk(path: str) -> str:
...     await asyncio.sleep(0.001)
...     return "Hello, world!"
...
>>> def transform(s: str) -> str:
...     return f"Length: {len(s)}"
...
>>> async def write_to_disk(s: str) -> None:
...     await asyncio.sleep(0.001)
...     print(f"Wrote '{s}' to disk.")
...
>>> async def read_and_transform_and_write(path: str) -> str:
...     p: Pipeline3[str, Awaitable[str], Awaitable[str], Awaitable[str]] = (
...         path,
...         read_from_disk,
...         a.map_(transform),
...         a.tap_to_awaitable(write_to_disk),
...     )
...     return await pipe(p)
...
>>> asyncio.run(read_and_transform_and_write("input.txt"))
Wrote 'Length: 13' to disk.
'Length: 13'

```

Use `awaitable_result.construct_from_result`
to widen a synchronously produced `trcks.Result` value into a
`trcks.AwaitableResult` value mid-pipeline, so that the pipeline can
continue with asynchronous, `trcks.Result`-returning functions:

```pycon
>>> def validate(n: int) -> Result[str, int]:
...     if n < 0:
...         return "failure", "negative value"
...     return "success", n
...
>>> async def get_square_root(x: float) -> Result[str, float]:
...     await asyncio.sleep(0.001)
...     return "success", x**0.5
...
>>> async def get_square_root_of_valid_number(n: int) -> Result[str, float]:
...     return await pipe(
...         (
...             validate(n),
...             ar.construct_from_result,
...             ar.map_success_to_awaitable_result(get_square_root),
...         )
...     )
...
>>> asyncio.run(get_square_root_of_valid_number(25))
('success', 5.0)
>>> asyncio.run(get_square_root_of_valid_number(-1))
('failure', 'negative value')

```

### Mapping inner values to awaitable values

Use `awaitable.map_` to apply a synchronous function to the value
wrapped in a `collections.abc.Awaitable`,
and `awaitable.map_to_awaitable` to apply an asynchronous function
instead:

```pycon
>>> awaitable_output = a.map_to_awaitable(write_to_disk)(
...     a.construct("Hello, world!")
... )
>>> asyncio.run(a.to_coroutine(awaitable_output))
Wrote 'Hello, world!' to disk.

```

Use `awaitable_result.map_success_to_awaitable_result`
to apply an asynchronous, `trcks.Result`-returning function
to the success value of a `trcks.AwaitableResult`:

```pycon
>>> a_rslt = ar.map_success_to_awaitable_result(get_square_root)(
...     ar.construct_success(25.0)
... )
>>> asyncio.run(ar.to_coroutine_result(a_rslt))
('success', 5.0)

```

Use `awaitable_tuple.map_to_awaitable`
to apply an asynchronous function to each element of an
`trcks.AwaitableTuple`:

```pycon
>>> async def slowly_add_one(n: int) -> int:
...     await asyncio.sleep(0.001)
...     return n + 1
...
>>> a_tpl = at.map_to_awaitable(slowly_add_one)(
...     at.construct_from_iterable((1, 2, 3))
... )
>>> asyncio.run(at.to_coroutine_tuple(a_tpl))
(2, 3, 4)

```

Use `awaitable_result_tuple.map_successes_to_awaitable_result_iterable`
to apply an asynchronous function with return type
`trcks.ResultIterable` to each success element of a
`trcks.AwaitableResultTuple`,
flattening the result and short-circuiting on the first failure:

```pycon
>>> async def duplicate_if_positive(n: int) -> ResultTuple[str, int]:
...     await asyncio.sleep(0.001)
...     if n > 0:
...         return "success", (n, n)
...     return "failure", "not positive"
...
>>> a_r_tpl = art.map_successes_to_awaitable_result_iterable(
...     duplicate_if_positive
... )(art.construct_successes_from_iterable((1, 2)))
>>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl))
('success', (1, 1, 2, 2))

```

### Tapping inner values with awaitable side effects

Use `awaitable.tap` and `awaitable.tap_to_awaitable`
to apply a synchronous or asynchronous side effect
without changing the value wrapped in a `collections.abc.Awaitable`:

```pycon
>>> async def slowly_log(n: int) -> None:
...     await asyncio.sleep(0.001)
...     print(f"Logged: {n}")
...
>>> awaitable_output = a.tap_to_awaitable(slowly_log)(a.construct(5))
>>> asyncio.run(a.to_coroutine(awaitable_output))
Logged: 5
5

```

Use `awaitable_result.tap_success_to_awaitable_result`
to execute an asynchronous side effect with return type
`trcks.AwaitableResult`:
a returned failure replaces the wrapped success value,
while a returned success leaves it unaffected.

```pycon
>>> async def persist_slowly(s: str) -> Result[str, None]:
...     await asyncio.sleep(0.001)
...     if len(s) > 10:
...         return "failure", "out of disk space"
...     return "success", None
...
>>> a_rslt = ar.tap_success_to_awaitable_result(persist_slowly)(
...     ar.construct_success("a very long string")
... )
>>> asyncio.run(ar.to_coroutine_result(a_rslt))
('failure', 'out of disk space')

```

`awaitable_result_tuple.tap_successes_to_awaitable_result`
works analogously for each success element of a
`trcks.AwaitableResultTuple`:

```pycon
>>> async def validate_positive_slowly(n: int) -> Result[str, None]:
...     await asyncio.sleep(0.001)
...     if n > 0:
...         return "success", None
...     return "failure", "not positive"
...
>>> a_r_tpl = art.tap_successes_to_awaitable_result(
...     validate_positive_slowly
... )(art.construct_successes_from_iterable((1, -1, 2)))
>>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl))
('failure', 'not positive')

```

### Unwrapping awaitable values

Each of the four modules provides a `to_coroutine*` function that turns
its `collections.abc.Awaitable` value into a `collections.abc.Coroutine`
value: `awaitable.to_coroutine`, `awaitable_result.to_coroutine_result`,
`awaitable_tuple.to_coroutine_tuple`, and
`awaitable_result_tuple.to_coroutine_result_tuple`.
On Python versions older than 3.14, `asyncio.run` expects a
`collections.abc.Coroutine` object, a subtype of
`collections.abc.Awaitable`.
Use these functions to convert before calling `asyncio.run`:

```pycon
>>> asyncio.run(a.to_coroutine(a.construct(42)))
42

```

## Further reading

Check the docstrings of the modules and functions in `trcks.fp` for more
explanations and examples.
