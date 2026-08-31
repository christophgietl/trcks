# Railway-oriented programming (ROP) with `trcks.oop`

The subpackage `trcks.oop` provides wrapper classes
for railway-oriented programming (ROP) in an object-oriented programming style
based on method chaining.

## Synchronous ROP with `trcks.oop`

### Classes for processing plain values, `trcks.Result` values, homogeneous tuples, and `trcks.ResultTuple` values

The class `BaseWrapper` is an immutable and generic wrapper class
with a single attribute.
This attribute is covariant:

```pycon
>>> import inspect
>>> from trcks.oop import BaseWrapper
>>> inspect.get_annotations(BaseWrapper)
{'core': +_T_co}

```

The classes `ResultTupleWrapper`, `ResultWrapper`, `TupleWrapper`, and `Wrapper`
are direct subclasses of `BaseWrapper`:

```pycon
>>> from trcks.oop import ResultTupleWrapper, ResultWrapper, TupleWrapper, Wrapper
>>> ResultTupleWrapper.__orig_bases__
(trcks.oop._base_wrapper.BaseWrapper[tuple[typing.Literal['failure'], +_F_default_co] | tuple[typing.Literal['success'], tuple[+_S_default_co, ...]]],)
>>> ResultWrapper.__orig_bases__
(trcks.oop._base_wrapper.BaseWrapper[tuple[typing.Literal['failure'], +_F_default_co] | tuple[typing.Literal['success'], +_S_default_co]],)
>>> TupleWrapper.__orig_bases__
(trcks.oop._base_wrapper.BaseWrapper[tuple[+_T_co, ...]],)
>>> Wrapper.__orig_bases__
(trcks.oop._base_wrapper.BaseWrapper[+_T_co],)

```

### Wrapping plain values, `trcks.Result` values, homogeneous tuples, and `trcks.ResultTuple` values

Do not use `BaseWrapper` to wrap any values:

```pycon
>>> greeting = "Hello, world!"
>>> base_wrapper: BaseWrapper[str] = BaseWrapper(core=greeting)  # Anti-pattern: do not do this.
>>> assert base_wrapper.core is greeting

```

Use `Wrapper` to wrap plain values:

```pycon
>>> wrapper: Wrapper[str] = Wrapper(core=greeting)
>>> assert wrapper.core is greeting

```

Use `ResultWrapper` to wrap `trcks.Result` values:

```pycon
>>> from trcks import Result
>>> result: Result[str, int] = ("success", 42)
>>> result_wrapper: ResultWrapper[str, int] = ResultWrapper(core=result)
>>> assert result_wrapper.core is result

```

Use `TupleWrapper` to wrap homogeneous tuples:

```pycon
>>> tpl = ("Hello", "world", "!")
>>> tuple_wrapper: TupleWrapper[str] = TupleWrapper(core=tpl)
>>> assert tuple_wrapper.core is tpl

```

Use `ResultTupleWrapper` to wrap `trcks.ResultTuple` values:

```pycon
>>> from trcks import ResultTuple
>>> result_tuple: ResultTuple[str, int] = ("success", (42, 43))
>>> result_tuple_wrapper: ResultTupleWrapper[str, int] = ResultTupleWrapper(core=result_tuple)
>>> assert result_tuple_wrapper.core is result_tuple

```

### Constructing `trcks.Result` values, tuples, and `trcks.ResultTuple` values from plain values

Use `ResultWrapper.construct_failure` or `ResultWrapper.construct_success`
to construct a `trcks.Result` object from a plain value and wrap it:

```pycon
>>> import sys
>>> if sys.version_info >= (3, 11):
...     from typing import Never
... else:
...     from typing_extensions import Never
>>> result_wrapper_1: ResultWrapper[str, Never] = ResultWrapper.construct_failure("Error")
>>> result_wrapper_1.core
('failure', 'Error')
>>> result_wrapper_2: ResultWrapper[Never, int] = ResultWrapper.construct_success(42)
>>> result_wrapper_2.core
('success', 42)

```

Use `TupleWrapper.construct` to construct a 1-element tuple from a plain value and
wrap it:

```pycon
>>> tuple_wrapper_1: TupleWrapper[int] = TupleWrapper.construct(42)
>>> tuple_wrapper_1.core
(42,)

```

Use `ResultTupleWrapper.construct_failure` or `ResultTupleWrapper.construct_successes`
to construct a `trcks.ResultTuple` object from a plain value and wrap it:

```pycon
>>> import sys
>>> if sys.version_info >= (3, 11):
...     from typing import Never
... else:
...     from typing_extensions import Never
>>> result_tuple_wrapper_1: ResultTupleWrapper[str, Never] = ResultTupleWrapper.construct_failure("Error")
>>> result_tuple_wrapper_1.core
('failure', 'Error')
>>> result_tuple_wrapper_2: ResultTupleWrapper[Never, int] = ResultTupleWrapper.construct_successes(42)
>>> result_tuple_wrapper_2.core
('success', (42,))

```

### Constructing homogeneous tuples and `trcks.ResultTuple` values from "complex" values

Use `TupleWrapper.construct_from_iterable` to construct a tuple
from a `collections.abc.Iterable` and wrap it:

```pycon
>>> print(inspect.signature(TupleWrapper.construct_from_iterable))
(it: 'Iterable[_T]') -> 'TupleWrapper[_T]'
>>> TupleWrapper.construct_from_iterable([1, 2, 3])
TupleWrapper(core=(1, 2, 3))

```

Use `ResultTupleWrapper.construct_from_*` or
`ResultTupleWrapper.construct_successes_from_iterable`
to construct a `trcks.ResultTuple` and wrap it:

```pycon
>>> print(inspect.signature(ResultTupleWrapper.construct_from_result))
(rslt: 'Result[_F_default, _S_default]') -> 'ResultTupleWrapper[_F_default, _S_default]'
>>> ResultTupleWrapper.construct_from_result(("success", 42))
ResultTupleWrapper(core=('success', (42,)))
>>> print(inspect.signature(ResultTupleWrapper.construct_from_result_iterable))
(r_it: 'ResultIterable[_F_default, _S_default]') -> 'ResultTupleWrapper[_F_default, _S_default]'
>>> ResultTupleWrapper.construct_from_result_iterable(("success", [42, 43]))
ResultTupleWrapper(core=('success', (42, 43)))
>>> print(inspect.signature(ResultTupleWrapper.construct_successes_from_iterable))
(it: 'Iterable[_S]') -> 'ResultTupleWrapper[Never, _S]'
>>> ResultTupleWrapper.construct_successes_from_iterable([42, 43])
ResultTupleWrapper(core=('success', (42, 43)))

```

### Mapping inner values to plain values

Use `Wrapper.map` to apply a function to the wrapped value and wrap the output:

```pycon
>>> print(inspect.signature(Wrapper.map))
(self, f: 'Callable[Concatenate[_T_co, _P], _T]', *args: '_P.args', **kwargs: '_P.kwargs') -> 'Wrapper[_T]'
>>> Wrapper(core="Hello, world!").map(len)
Wrapper(core=13)
>>> # `map` methods pass additional arguments to the applied function:
>>> Wrapper(core=3.14).map(round, ndigits=1)
Wrapper(core=3.1)

```

Use `ResultWrapper.map_failure` and `ResultWrapper.map_success`
to apply functions to the failure or success value of a result and wrap the output:

```pycon
>>> print(inspect.signature(ResultWrapper.map_failure))
(self, f: 'Callable[Concatenate[_F_default_co, _P], _F]', *args: '_P.args', **kwargs: '_P.kwargs') -> 'ResultWrapper[_F, _S_default_co]'
>>> ResultWrapper.construct_failure("negative value").map_failure(
...     lambda s: f"Prefix: {s}"
... )
ResultWrapper(core=('failure', 'Prefix: negative value'))
>>> ResultWrapper.construct_success(42).map_failure(
...     lambda s: f"Prefix: {s}"
... )
ResultWrapper(core=('success', 42))
>>> print(inspect.signature(ResultWrapper.map_success))
(self, f: 'Callable[Concatenate[_S_default_co, _P], _S]', *args: '_P.args', **kwargs: '_P.kwargs') -> 'ResultWrapper[_F_default_co, _S]'
>>> ResultWrapper.construct_failure("negative value").map_success(
...     lambda n: n + 1
... )
ResultWrapper(core=('failure', 'negative value'))
>>> ResultWrapper.construct_success(42).map_success(lambda n: n + 1)
ResultWrapper(core=('success', 43))

```

Use `TupleWrapper.map` to apply a function to each element in the wrapped
tuple and wrap the output:

```pycon
>>> print(inspect.signature(TupleWrapper.map))
(self, f: 'Callable[Concatenate[_T_co, _P], _T]', *args: '_P.args', **kwargs: '_P.kwargs') -> 'TupleWrapper[_T]'
>>> TupleWrapper.construct_from_iterable(("a", "bb", "ccc")).map(len)
TupleWrapper(core=(1, 2, 3))

```

Use `ResultTupleWrapper.map_failure` and `ResultTupleWrapper.map_successes`
to apply functions to the failure or success values of a result tuple and
wrap the output:

```pycon
>>> print(inspect.signature(ResultTupleWrapper.map_failure))
(self, f: 'Callable[Concatenate[_F_default_co, _P], _F]', *args: '_P.args', **kwargs: '_P.kwargs') -> 'ResultTupleWrapper[_F, _S_default_co]'
>>> ResultTupleWrapper.construct_failure("not found").map_failure(
...     lambda s: f"err: {s}"
... )
ResultTupleWrapper(core=('failure', 'err: not found'))
>>> print(inspect.signature(ResultTupleWrapper.map_successes))
(self, f: 'Callable[Concatenate[_S_default_co, _P], _S]', *args: '_P.args', **kwargs: '_P.kwargs') -> 'ResultTupleWrapper[_F_default_co, _S]'
>>> ResultTupleWrapper.construct_successes_from_iterable((1, 2, 3)).map_successes(
...     lambda n: n * 2
... )
ResultTupleWrapper(core=('success', (2, 4, 6)))

```

### Mapping inner values to "complex" values

Use `Wrapper.map_to_result` to apply a function returning `trcks.Result`
to the wrapped value and wrap the output:

```pycon
>>> print(inspect.signature(Wrapper.map_to_result))
(self, f: 'Callable[Concatenate[_T_co, _P], Result[_F, _S]]', *args: '_P.args', **kwargs: '_P.kwargs') -> 'ResultWrapper[_F, _S]'
>>> Wrapper.construct(-1).map_to_result(
...     lambda n: ("success", n)
...     if n >= 0
...     else ("failure", "negative value")
... )
ResultWrapper(core=('failure', 'negative value'))

```

Use `Wrapper.map_to_iterable` to apply a function returning
a `collections.abc.Iterable` to the wrapped value and wrap the output:

```pycon
>>> print(inspect.signature(Wrapper.map_to_iterable))
(self, f: 'Callable[Concatenate[_T_co, _P], Iterable[_T]]', *args: '_P.args', **kwargs: '_P.kwargs') -> 'TupleWrapper[_T]'
>>> def duplicate(n: int) -> tuple[int, int]:
...     return n, n
...
>>> Wrapper.construct(3).map_to_iterable(duplicate)
TupleWrapper(core=(3, 3))

```

Use `ResultWrapper.map_failure_to_result` and `ResultWrapper.map_success_to_result`
to apply functions with return type `trcks.Result` to the failure or success
value of a result and wrap the output:

```pycon
>>> import math
>>> from trcks import Result
>>> from trcks.oop import ResultWrapper
>>> def replace_not_found_by_default_value(s: str) -> Result[str, float]:
...     if s == "not found":
...         return "success", 0.0
...     return "failure", s
...
>>> print(inspect.signature(ResultWrapper.map_failure_to_result))
(self, f: 'Callable[Concatenate[_F_default_co, _P], Result[_F, _S]]', *args: '_P.args', **kwargs: '_P.kwargs') -> 'ResultWrapper[_F, _S_default_co | _S]'
>>> ResultWrapper.construct_failure("not found").map_failure_to_result(
...     replace_not_found_by_default_value
... )
ResultWrapper(core=('success', 0.0))
>>> ResultWrapper.construct_success(42).map_failure_to_result(
...     replace_not_found_by_default_value
... )
ResultWrapper(core=('success', 42))
>>> def get_square_root(x: float) -> Result[str, float]:
...     if x < 0:
...         return "failure", "negative value"
...     return "success", math.sqrt(x)
...
>>> print(inspect.signature(ResultWrapper.map_success_to_result))
(self, f: 'Callable[Concatenate[_S_default_co, _P], Result[_F, _S]]', *args: '_P.args', **kwargs: '_P.kwargs') -> 'ResultWrapper[_F_default_co | _F, _S]'
>>> ResultWrapper.construct_failure("not found").map_success_to_result(
...     get_square_root
... )
ResultWrapper(core=('failure', 'not found'))
>>> ResultWrapper.construct_success(25.0).map_success_to_result(get_square_root)
ResultWrapper(core=('success', 5.0))

```

Use `ResultWrapper.map_failure_to_iterable` and `ResultWrapper.map_success_to_iterable`
to apply functions returning a `collections.abc.Iterable` to the failure or success
value of a result and wrap the output:

```pycon
>>> def recover(s: str) -> tuple[float, ...]:
...     if s == "not found":
...         return (0.0, 1.0)
...     return ()
...
>>> print(inspect.signature(ResultWrapper.map_failure_to_iterable))
(self, f: 'Callable[Concatenate[_F_default_co, _P], Iterable[_S]]', *args: '_P.args', **kwargs: '_P.kwargs') -> 'ResultTupleWrapper[Never, _S_default_co | _S]'
>>> ResultWrapper.construct_failure("not found").map_failure_to_iterable(recover)
ResultTupleWrapper(core=('success', (0.0, 1.0)))
>>> ResultWrapper.construct_success(42).map_failure_to_iterable(recover)
ResultTupleWrapper(core=('success', (42,)))
>>> def duplicate(n: int) -> tuple[int, int]:
...     return n, n
...
>>> print(inspect.signature(ResultWrapper.map_success_to_iterable))
(self, f: 'Callable[Concatenate[_S_default_co, _P], Iterable[_S]]', *args: '_P.args', **kwargs: '_P.kwargs') -> 'ResultTupleWrapper[_F_default_co, _S]'
>>> ResultWrapper.construct_failure("not found").map_success_to_iterable(duplicate)
ResultTupleWrapper(core=('failure', 'not found'))
>>> ResultWrapper.construct_success(5).map_success_to_iterable(duplicate)
ResultTupleWrapper(core=('success', (5, 5)))

```

Use `TupleWrapper.map_to_result` to apply a function with return type `trcks.Result`
to each element in the wrapped tuple and wrap the output:

```pycon
>>> from trcks.oop import TupleWrapper
>>> def double_if_positive(n: int) -> Result[str, int]:
...     if n > 0:
...         return "success", n * 2
...     return "failure", "not positive"
...
>>> print(inspect.signature(TupleWrapper.map_to_result))
(self, f: 'Callable[Concatenate[_T_co, _P], Result[_F, _S]]', *args: '_P.args', **kwargs: '_P.kwargs') -> 'ResultTupleWrapper[_F, _S]'
>>> TupleWrapper.construct_from_iterable((1, 2, 3)).map_to_result(double_if_positive)
ResultTupleWrapper(core=('success', (2, 4, 6)))
>>> TupleWrapper.construct_from_iterable((1, -1, 2)).map_to_result(double_if_positive)
ResultTupleWrapper(core=('failure', 'not positive'))

```

Use `TupleWrapper.map_to_iterable` to apply a function returning
a `collections.abc.Iterable` to each element in the wrapped tuple
and flatten the result:

```pycon
>>> def duplicate_integer(n: int) -> tuple[int, int]:
...     return n, n
...
>>> print(inspect.signature(TupleWrapper.map_to_iterable))
(self, f: 'Callable[Concatenate[_T_co, _P], Iterable[_T]]', *args: '_P.args', **kwargs: '_P.kwargs') -> 'TupleWrapper[_T]'
>>> TupleWrapper.construct_from_iterable((1, 2, 3)).map_to_iterable(duplicate_integer)
TupleWrapper(core=(1, 1, 2, 2, 3, 3))

```

Use `ResultTupleWrapper.map_failure_to_result` and `ResultTupleWrapper.map_successes_to_result`
to apply functions with return type `trcks.Result` to the failure or success
values of a result tuple and wrap the output:

```pycon
>>> from trcks.oop import ResultTupleWrapper
>>> def recover_from_not_found(description: str) -> Result[str, int]:
...     if description == "not found":
...         return "success", 0
...     return "failure", description
...
>>> print(inspect.signature(ResultTupleWrapper.map_failure_to_result))
(self, f: 'Callable[Concatenate[_F_default_co, _P], Result[_F, _S]]', *args: '_P.args', **kwargs: '_P.kwargs') -> 'ResultTupleWrapper[_F, _S_default_co | _S]'
>>> ResultTupleWrapper.construct_failure("not found").map_failure_to_result(
...     recover_from_not_found
... )
ResultTupleWrapper(core=('success', (0,)))
>>> ResultTupleWrapper.construct_successes_from_iterable((1, 2)).map_failure_to_result(
...     recover_from_not_found
... )
ResultTupleWrapper(core=('success', (1, 2)))
>>> def double_if_positive(n: int) -> Result[str, int]:
...     if n > 0:
...         return "success", n * 2
...     return "failure", "not positive"
...
>>> print(inspect.signature(ResultTupleWrapper.map_successes_to_result))
(self, f: 'Callable[Concatenate[_S_default_co, _P], Result[_F, _S]]', *args: '_P.args', **kwargs: '_P.kwargs') -> 'ResultTupleWrapper[_F_default_co | _F, _S]'
>>> ResultTupleWrapper.construct_successes_from_iterable((1, 2)).map_successes_to_result(
...     double_if_positive
... )
ResultTupleWrapper(core=('success', (2, 4)))
>>> ResultTupleWrapper.construct_successes_from_iterable((1, -1, 2)).map_successes_to_result(
...     double_if_positive
... )
ResultTupleWrapper(core=('failure', 'not positive'))

```

Use `ResultTupleWrapper.map_failure_to_iterable` and `ResultTupleWrapper.map_successes_to_iterable`
to apply functions returning a `collections.abc.Iterable` to the failure or success
values of a result tuple and flatten the result:

```pycon
>>> def recover_from_not_found_iterable(description: str) -> tuple[int, ...]:
...     if description == "not found":
...         return (0,)
...     return ()
...
>>> print(inspect.signature(ResultTupleWrapper.map_failure_to_iterable))
(self, f: 'Callable[Concatenate[_F_default_co, _P], Iterable[_S]]', *args: '_P.args', **kwargs: '_P.kwargs') -> 'ResultTupleWrapper[Never, _S_default_co | _S]'
>>> ResultTupleWrapper.construct_failure("not found").map_failure_to_iterable(
...     recover_from_not_found_iterable
... )
ResultTupleWrapper(core=('success', (0,)))
>>> ResultTupleWrapper.construct_successes_from_iterable((1, 2)).map_failure_to_iterable(
...     recover_from_not_found_iterable
... )
ResultTupleWrapper(core=('success', (1, 2)))
>>> def duplicate_integer(n: int) -> tuple[int, int]:
...     return n, n
...
>>> print(inspect.signature(ResultTupleWrapper.map_successes_to_iterable))
(self, f: 'Callable[Concatenate[_S_default_co, _P], Iterable[_S]]', *args: '_P.args', **kwargs: '_P.kwargs') -> 'ResultTupleWrapper[_F_default_co, _S]'
>>> ResultTupleWrapper.construct_successes_from_iterable((1, 2)).map_successes_to_iterable(
...     duplicate_integer
... )
ResultTupleWrapper(core=('success', (1, 1, 2, 2)))
>>> ResultTupleWrapper.construct_failure("not found").map_successes_to_iterable(
...     duplicate_integer
... )
ResultTupleWrapper(core=('failure', 'not found'))

```

### Tapping inner values with plain side effects

Tapping applies a side effect (e.g. logging) to a wrapped value
without changing it.
Unlike `map*` methods, `tap*` methods always return
a new wrapper with the original, unmodified value,
allowing side effects to be inserted into a chain of method calls.

Use `Wrapper.tap` to apply a side effect to the wrapped value:

```pycon
>>> print(inspect.signature(Wrapper.tap))
(self, f: 'Callable[Concatenate[_T_co, _P], object]', *args: '_P.args', **kwargs: '_P.kwargs') -> 'Wrapper[_T_co]'
>>> wrapper = Wrapper.construct(5).tap(lambda n: print(f"Number: {n}"))
Number: 5
>>> wrapper
Wrapper(core=5)

```

Use `ResultWrapper.tap_failure` and `ResultWrapper.tap_success`
to apply side effects to the failure or success value of a result:

```pycon
>>> print(inspect.signature(ResultWrapper.tap_failure))
(self, f: 'Callable[Concatenate[_F_default_co, _P], object]', *args: '_P.args', **kwargs: '_P.kwargs') -> 'ResultWrapper[_F_default_co, _S_default_co]'
>>> ResultWrapper.construct_failure("not found").tap_failure(
...     lambda f: print(f"Failure: {f}")
... )
Failure: not found
ResultWrapper(core=('failure', 'not found'))
>>> ResultWrapper.construct_success(42).tap_failure(
...     lambda f: print(f"Failure: {f}")
... )
ResultWrapper(core=('success', 42))
>>> print(inspect.signature(ResultWrapper.tap_success))
(self, f: 'Callable[Concatenate[_S_default_co, _P], object]', *args: '_P.args', **kwargs: '_P.kwargs') -> 'ResultWrapper[_F_default_co, _S_default_co]'
>>> ResultWrapper.construct_failure("not found").tap_success(
...     lambda n: print(f"Number: {n}")
... )
ResultWrapper(core=('failure', 'not found'))
>>> ResultWrapper.construct_success(42).tap_success(
...     lambda n: print(f"Number: {n}")
... )
Number: 42
ResultWrapper(core=('success', 42))

```

Use `TupleWrapper.tap` to apply a side effect to each element
in the wrapped tuple:

```pycon
>>> print(inspect.signature(TupleWrapper.tap))
(self, f: 'Callable[Concatenate[_T_co, _P], object]', *args: '_P.args', **kwargs: '_P.kwargs') -> 'TupleWrapper[_T_co]'
>>> def log_integer(n: int) -> None:
...     print(f"Received: {n}")
...
>>> TupleWrapper.construct_from_iterable((1, 2, 3)).tap(log_integer)
Received: 1
Received: 2
Received: 3
TupleWrapper(core=(1, 2, 3))

```

Use `ResultTupleWrapper.tap_failure` and `ResultTupleWrapper.tap_successes`
to apply side effects to the failure or success values of a result tuple:

```pycon
>>> print(inspect.signature(ResultTupleWrapper.tap_failure))
(self, f: 'Callable[Concatenate[_F_default_co, _P], object]', *args: '_P.args', **kwargs: '_P.kwargs') -> 'ResultTupleWrapper[_F_default_co, _S_default_co]'
>>> def log_error(description: str) -> None:
...     print(f"Error: {description}")
...
>>> ResultTupleWrapper.construct_failure("oops").tap_failure(log_error)
Error: oops
ResultTupleWrapper(core=('failure', 'oops'))
>>> ResultTupleWrapper.construct_successes(1).tap_failure(log_error)
ResultTupleWrapper(core=('success', (1,)))
>>> print(inspect.signature(ResultTupleWrapper.tap_successes))
(self, f: 'Callable[Concatenate[_S_default_co, _P], object]', *args: '_P.args', **kwargs: '_P.kwargs') -> 'ResultTupleWrapper[_F_default_co, _S_default_co]'
>>> ResultTupleWrapper.construct_successes_from_iterable(
...     (1, 2)
... ).tap_successes(log_integer)
Received: 1
Received: 2
ResultTupleWrapper(core=('success', (1, 2)))
>>> ResultTupleWrapper.construct_failure("oops").tap_successes(log_integer)
ResultTupleWrapper(core=('failure', 'oops'))

```

### Tapping inner values with "complex" side effects

The `tap*` methods shown above discard the return value of the side effect.
`tap_to_result`, `tap_failure_to_result`, and `tap_success*_to_result` methods
apply a side effect with return type `trcks.Result` instead.
For `tap_to_result` and `tap_success*_to_result`,
a returned `trcks.Failure` replaces the current value on the failure track,
while a returned `trcks.Success` leaves the tapped value unaffected.
`tap_failure_to_result` reverses these roles:
a returned `trcks.Success` replaces the current value on the success track,
while a returned `trcks.Failure` leaves the tapped value unaffected.
Similarly, `tap_to_iterable`, `tap_failure_to_iterable`, and `tap_success*_to_iterable`
methods apply a side effect returning a `collections.abc.Iterable`,
repeating the tapped value once per item returned by the side effect.

Use `Wrapper.tap_to_result` to apply such a side effect
to the wrapped value:

```pycon
>>> from trcks import Result
>>> print(inspect.signature(Wrapper.tap_to_result))
(self, f: 'Callable[Concatenate[_T_co, _P], Result[_F, object]]', *args: '_P.args', **kwargs: '_P.kwargs') -> 'ResultWrapper[_F, _T_co]'
>>> def print_positive_float(x: float) -> Result[str, None]:
...     if x <= 0:
...         return "failure", "not positive"
...     return "success", print(f"Positive float: {x}")
...
>>> Wrapper.construct(-2.3).tap_to_result(print_positive_float)
ResultWrapper(core=('failure', 'not positive'))
>>> Wrapper.construct(3.5).tap_to_result(print_positive_float)
Positive float: 3.5
ResultWrapper(core=('success', 3.5))

```

Use `Wrapper.tap_to_iterable` to repeat the wrapped value
once per item returned by the side effect:

```pycon
>>> print(inspect.signature(Wrapper.tap_to_iterable))
(self, f: 'Callable[Concatenate[_T_co, _P], Iterable[object]]', *args: '_P.args', **kwargs: '_P.kwargs') -> 'TupleWrapper[_T_co]'
>>> def write_to_disk(n: int) -> tuple[str, str]:
...     print(f"Wrote {n} to disk.")
...     return "left", "right"
...
>>> Wrapper.construct(3).tap_to_iterable(write_to_disk)
Wrote 3 to disk.
TupleWrapper(core=(3, 3))

```

Use `ResultWrapper.tap_failure_to_result` to apply a side effect
with return type `trcks.Result` to the wrapped `Failure` object,
optionally recovering it into a `Success`:

```pycon
>>> print(inspect.signature(ResultWrapper.tap_failure_to_result))
(self, f: 'Callable[Concatenate[_F_default_co, _P], Result[object, _S]]', *args: '_P.args', **kwargs: '_P.kwargs') -> 'ResultWrapper[_F_default_co, _S_default_co | _S]'
>>> def replace_not_found_with_default(s: str) -> Result[object, float]:
...     if s == "not found":
...         return "success", 0.0
...     return "failure", s
...
>>> ResultWrapper.construct_failure("not found").tap_failure_to_result(
...     replace_not_found_with_default
... )
ResultWrapper(core=('success', 0.0))
>>> ResultWrapper.construct_failure("other error").tap_failure_to_result(
...     replace_not_found_with_default
... )
ResultWrapper(core=('failure', 'other error'))
>>> ResultWrapper.construct_success(42).tap_failure_to_result(
...     replace_not_found_with_default
... )
ResultWrapper(core=('success', 42))

```

Use `ResultTupleWrapper.tap_successes_to_result` to apply a side effect
with return type `trcks.Result` to each element in the wrapped
`SuccessTuple`, letting any returned `Failure` short-circuit the tuple:

```pycon
>>> print(inspect.signature(ResultTupleWrapper.tap_successes_to_result))
(self, f: 'Callable[Concatenate[_S_default_co, _P], Result[_F, object]]', *args: '_P.args', **kwargs: '_P.kwargs') -> 'ResultTupleWrapper[_F_default_co | _F, _S_default_co]'
>>> def validate_positive(n: int) -> Result[str, None]:
...     if n > 0:
...         return "success", None
...     return "failure", "not positive"
...
>>> ResultTupleWrapper.construct_successes_from_iterable(
...     (1, 2)
... ).tap_successes_to_result(validate_positive)
ResultTupleWrapper(core=('success', (1, 2)))
>>> ResultTupleWrapper.construct_successes_from_iterable(
...     (1, -1, 2)
... ).tap_successes_to_result(validate_positive)
ResultTupleWrapper(core=('failure', 'not positive'))
>>> ResultTupleWrapper.construct_failure("oops").tap_successes_to_result(
...     validate_positive
... )
ResultTupleWrapper(core=('failure', 'oops'))

```

## Asynchronous ROP with `trcks.oop`

### Classes for processing awaitable values, `trcks.AwaitableResult` values, awaitable tuples, and `trcks.AwaitableResultTuple` values

The class `BaseAwaitableWrapper` is analogous to `BaseWrapper`,
but wraps a `collections.abc.Awaitable` object instead of a plain value:

```pycon
>>> from trcks.oop import BaseAwaitableWrapper
>>> BaseAwaitableWrapper.__orig_bases__
(trcks.oop._base_wrapper.BaseWrapper[collections.abc.Awaitable[+_T_co]],)

```

The classes `AwaitableResultTupleWrapper`, `AwaitableResultWrapper`,
`AwaitableTupleWrapper`, and `AwaitableWrapper`
are direct subclasses of `BaseAwaitableWrapper`:

```pycon
>>> from trcks.oop import (
...     AwaitableResultTupleWrapper,
...     AwaitableResultWrapper,
...     AwaitableTupleWrapper,
...     AwaitableWrapper,
... )
>>> AwaitableResultTupleWrapper.__orig_bases__
(trcks.oop._base_awaitable_wrapper.BaseAwaitableWrapper[tuple[typing.Literal['failure'], +_F_default_co] | tuple[typing.Literal['success'], tuple[+_S_default_co, ...]]],)
>>> AwaitableResultWrapper.__orig_bases__
(trcks.oop._base_awaitable_wrapper.BaseAwaitableWrapper[tuple[typing.Literal['failure'], +_F_default_co] | tuple[typing.Literal['success'], +_S_default_co]],)
>>> AwaitableTupleWrapper.__orig_bases__
(trcks.oop._base_awaitable_wrapper.BaseAwaitableWrapper[tuple[+_T_co, ...]],)
>>> AwaitableWrapper.__orig_bases__
(trcks.oop._base_awaitable_wrapper.BaseAwaitableWrapper[+_T_co],)

```

Just like `BaseWrapper`, `BaseAwaitableWrapper` should not be used directly.
Its subclasses share the same `map*` and `tap*` naming conventions
introduced in the section above
(single value versus failure and success versus tuple and success tuple);
this section only covers what is specific to awaitable values.

### Constructing awaitable values, `trcks.AwaitableResult` values, awaitable tuples, and `trcks.AwaitableResultTuple` values

Use `AwaitableWrapper.construct_from_awaitable` (or the default constructor)
to wrap an existing `collections.abc.Awaitable` object:

```pycon
>>> import asyncio
>>> async def read_from_disk() -> str:
...     await asyncio.sleep(0.001)
...     return "Hello, world!"
...
>>> print(inspect.signature(AwaitableWrapper.construct_from_awaitable))
(awtbl: 'Awaitable[_T]') -> 'AwaitableWrapper[_T]'
>>> awaitable_wrapper = AwaitableWrapper.construct_from_awaitable(read_from_disk())
>>> awaitable_wrapper
AwaitableWrapper(core=<coroutine object ...>)
>>> asyncio.run(awaitable_wrapper.core_as_coroutine)
'Hello, world!'

```

Use `AwaitableWrapper.construct` to wrap a plain value
in an already resolved `collections.abc.Awaitable` object:

```pycon
>>> print(inspect.signature(AwaitableWrapper.construct))
(value: '_T') -> 'AwaitableWrapper[_T]'
>>> asyncio.run(AwaitableWrapper.construct(42).core_as_coroutine)
42

```

`AwaitableResultWrapper`, `AwaitableTupleWrapper`, and `AwaitableResultTupleWrapper`
provide analogous `construct*` factories,
including `*_from_awaitable` variants for each of them.
Use `AwaitableResultWrapper.construct_success_from_awaitable`
(or `.construct_failure_from_awaitable`)
to construct a `trcks.AwaitableResult` object from an awaitable value:

```pycon
>>> from trcks.oop import AwaitableResultWrapper
>>> print(inspect.signature(AwaitableResultWrapper.construct_success_from_awaitable))
(awtbl: 'Awaitable[_S]') -> 'AwaitableResultWrapper[Never, _S]'
>>> awaitable_result_wrapper = AwaitableResultWrapper.construct_success_from_awaitable(
...     read_from_disk()
... )
>>> awaitable_result_wrapper
AwaitableResultWrapper(core=<coroutine object ...>)
>>> asyncio.run(awaitable_result_wrapper.core_as_coroutine)
('success', 'Hello, world!')

```

Use `AwaitableTupleWrapper.construct_from_iterable`
to construct a `trcks.AwaitableTuple` object from a plain `collections.abc.Iterable`:

```pycon
>>> print(inspect.signature(AwaitableTupleWrapper.construct_from_iterable))
(it: 'Iterable[_T]') -> 'AwaitableTupleWrapper[_T]'
>>> asyncio.run(
...     AwaitableTupleWrapper.construct_from_iterable([1, 2, 3]).core_as_coroutine
... )
(1, 2, 3)

```

Use `AwaitableResultTupleWrapper.construct_successes_from_iterable`
to construct a `trcks.AwaitableResultTuple` object from a plain `collections.abc.Iterable`:

```pycon
>>> print(inspect.signature(AwaitableResultTupleWrapper.construct_successes_from_iterable))
(it: 'Iterable[_S]') -> 'AwaitableResultTupleWrapper[Never, _S]'
>>> asyncio.run(
...     AwaitableResultTupleWrapper.construct_successes_from_iterable(
...         [1, 2]
...     ).core_as_coroutine
... )
('success', (1, 2))

```

### Entering the async track from a synchronous wrapper

`Wrapper`, `ResultWrapper`, `TupleWrapper`, and `ResultTupleWrapper`
provide `map_to_awaitable*` and `tap_to_awaitable*` methods
that apply a `collections.abc.Awaitable`-returning function
and switch to the corresponding asynchronous wrapper class.
Use `Wrapper.map_to_awaitable` to switch from `Wrapper` to `AwaitableWrapper`:

```pycon
>>> print(inspect.signature(Wrapper.map_to_awaitable))
(self, f: 'Callable[Concatenate[_T_co, _P], Awaitable[_T]]', *args: '_P.args', **kwargs: '_P.kwargs') -> 'AwaitableWrapper[_T]'
>>> async def write_to_disk(s: str) -> None:
...     await asyncio.sleep(0.001)
...     print(f"Wrote '{s}' to disk.")
...
>>> awaitable_wrapper = Wrapper.construct("Hello, world!").map_to_awaitable(
...     write_to_disk
... )
>>> awaitable_wrapper
AwaitableWrapper(core=<coroutine object ...>)
>>> asyncio.run(awaitable_wrapper.core_as_coroutine)
Wrote 'Hello, world!' to disk.

```

Use `ResultWrapper.map_success_to_awaitable_result`
to switch from `ResultWrapper` to `AwaitableResultWrapper`:

```pycon
>>> from trcks import Result
>>> from trcks.oop import ResultWrapper
>>> print(inspect.signature(ResultWrapper.map_success_to_awaitable_result))
(self, f: 'Callable[Concatenate[_S_default_co, _P], AwaitableResult[_F, _S]]', *args: '_P.args', **kwargs: '_P.kwargs') -> 'AwaitableResultWrapper[_F_default_co | _F, _S]'
>>> async def get_square_root(x: float) -> Result[str, float]:
...     await asyncio.sleep(0.001)
...     if x < 0:
...         return "failure", "negative value"
...     return "success", x**0.5
...
>>> awaitable_result_wrapper = ResultWrapper.construct_success(
...     25.0
... ).map_success_to_awaitable_result(get_square_root)
>>> awaitable_result_wrapper
AwaitableResultWrapper(core=<coroutine object ...>)
>>> asyncio.run(awaitable_result_wrapper.core_as_coroutine)
('success', 5.0)

```

`TupleWrapper.map_to_awaitable` and `ResultTupleWrapper.map_successes_to_awaitable_result`
work analogously,
switching to `AwaitableTupleWrapper` and `AwaitableResultTupleWrapper`, respectively.

### Mapping inner values to awaitable values

Most `map*` methods documented in the synchronous section above
have `_to_awaitable`, `_to_awaitable_iterable`, `_to_awaitable_result`,
and `_to_awaitable_result_iterable` counterparts
that apply an asynchronous, instead of a synchronous, function,
but not every wrapper supports the full set of counterparts
for every method
(e.g. `ResultWrapper.map_failure` has no `map_failure_to_awaitable_iterable` counterpart).
These counterparts are also available on the four asynchronous wrapper classes,
allowing an already asynchronous chain to continue.

Use `AwaitableWrapper.map_to_awaitable` to chain another asynchronous function:

```pycon
>>> print(inspect.signature(AwaitableWrapper.map_to_awaitable))
(self, f: 'Callable[Concatenate[_T_co, _P], Awaitable[_T]]', *args: '_P.args', **kwargs: '_P.kwargs') -> 'AwaitableWrapper[_T]'
>>> async def slowly_add_one(n: int) -> int:
...     await asyncio.sleep(0.001)
...     return n + 1
...
>>> awaitable_wrapper = AwaitableWrapper.construct(41).map_to_awaitable(
...     slowly_add_one
... )
>>> awaitable_wrapper
AwaitableWrapper(core=<coroutine object ...>)
>>> asyncio.run(awaitable_wrapper.core_as_coroutine)
42

```

Use `AwaitableResultWrapper.map_success_to_awaitable_result`
to apply an asynchronous, failable function to the wrapped success value:

```pycon
>>> print(inspect.signature(AwaitableResultWrapper.map_success_to_awaitable_result))
(self, f: 'Callable[Concatenate[_S_default_co, _P], AwaitableResult[_F, _S]]', *args: '_P.args', **kwargs: '_P.kwargs') -> 'AwaitableResultWrapper[_F_default_co | _F, _S]'
>>> awaitable_result_wrapper_1 = AwaitableResultWrapper.construct_success(
...     25.0
... ).map_success_to_awaitable_result(get_square_root)
>>> awaitable_result_wrapper_1
AwaitableResultWrapper(core=<coroutine object ...>)
>>> asyncio.run(awaitable_result_wrapper_1.core_as_coroutine)
('success', 5.0)
>>> awaitable_result_wrapper_2 = AwaitableResultWrapper.construct_failure(
...     "not found"
... ).map_success_to_awaitable_result(get_square_root)
>>> awaitable_result_wrapper_2
AwaitableResultWrapper(core=<coroutine object ...>)
>>> asyncio.run(awaitable_result_wrapper_2.core_as_coroutine)
('failure', 'not found')

```

Use `AwaitableTupleWrapper.map_to_awaitable`
to apply an asynchronous function to each element in the wrapped tuple:

```pycon
>>> from trcks.oop import AwaitableTupleWrapper
>>> print(inspect.signature(AwaitableTupleWrapper.map_to_awaitable))
(self, f: 'Callable[Concatenate[_T_co, _P], Awaitable[_T]]', *args: '_P.args', **kwargs: '_P.kwargs') -> 'AwaitableTupleWrapper[_T]'
>>> awaitable_tuple_wrapper = AwaitableTupleWrapper.construct_from_iterable(
...     (1, 2, 3)
... ).map_to_awaitable(slowly_add_one)
>>> awaitable_tuple_wrapper
AwaitableTupleWrapper(core=<coroutine object ...>)
>>> asyncio.run(awaitable_tuple_wrapper.core_as_coroutine)
(2, 3, 4)

```

Use `AwaitableResultTupleWrapper.map_successes_to_awaitable_result_iterable`
to apply an asynchronous function with return type `trcks.ResultIterable`
to each element in the wrapped success tuple,
flattening the result and short-circuiting on the first failure:

```pycon
>>> from trcks import ResultTuple
>>> from trcks.oop import AwaitableResultTupleWrapper
>>> print(inspect.signature(AwaitableResultTupleWrapper.map_successes_to_awaitable_result_iterable))
(self, f: 'Callable[Concatenate[_S_default_co, _P], AwaitableResultIterable[_F, _S]]', *args: '_P.args', **kwargs: '_P.kwargs') -> 'AwaitableResultTupleWrapper[_F_default_co | _F, _S]'
>>> async def duplicate_if_positive(n: int) -> ResultTuple[str, int]:
...     await asyncio.sleep(0.001)
...     if n <= 0:
...         return "failure", "not positive"
...     return "success", (n, n)
...
>>> wrapper_1 = AwaitableResultTupleWrapper.construct_successes_from_iterable(
...     (1, 2)
... ).map_successes_to_awaitable_result_iterable(duplicate_if_positive)
>>> wrapper_1
AwaitableResultTupleWrapper(core=<coroutine object ...>)
>>> asyncio.run(wrapper_1.core_as_coroutine)
('success', (1, 1, 2, 2))
>>> wrapper_2 = AwaitableResultTupleWrapper.construct_successes_from_iterable(
...     (1, -1, 2)
... ).map_successes_to_awaitable_result_iterable(duplicate_if_positive)
>>> wrapper_2
AwaitableResultTupleWrapper(core=<coroutine object ...>)
>>> asyncio.run(wrapper_2.core_as_coroutine)
('failure', 'not positive')

```

### Tapping inner values with awaitable side effects

Just like the `_to_awaitable*` suffixes for `map*` methods,
most `tap*` methods gain `_to_awaitable`, `_to_awaitable_iterable`,
`_to_awaitable_result`, and `_to_awaitable_result_iterable` counterparts
for executing asynchronous side effects,
but not every wrapper supports the full set of counterparts
for every method
(e.g. `ResultWrapper.tap_failure` has no `tap_failure_to_awaitable_iterable` counterpart).

Use `AwaitableWrapper.tap_to_awaitable`
to execute an asynchronous side effect without changing the wrapped value:

```pycon
>>> print(inspect.signature(AwaitableWrapper.tap_to_awaitable))
(self, f: 'Callable[Concatenate[_T_co, _P], Awaitable[object]]', *args: '_P.args', **kwargs: '_P.kwargs') -> 'AwaitableWrapper[_T_co]'
>>> async def slowly_log(n: int) -> None:
...     await asyncio.sleep(0.001)
...     print(f"Logged: {n}")
...
>>> awaitable_wrapper = AwaitableWrapper.construct(5).tap_to_awaitable(slowly_log)
>>> awaitable_wrapper
AwaitableWrapper(core=<coroutine object ...>)
>>> asyncio.run(awaitable_wrapper.core_as_coroutine)
Logged: 5
5

```

Use `AwaitableResultWrapper.tap_success_to_awaitable_result`
to execute an asynchronous side effect with return type `trcks.AwaitableResult`:
a returned `trcks.Failure` replaces the wrapped success value,
while a returned `trcks.Success` leaves it unaffected:

```pycon
>>> print(inspect.signature(AwaitableResultWrapper.tap_success_to_awaitable_result))
(self, f: 'Callable[Concatenate[_S_default_co, _P], AwaitableResult[_F, object]]', *args: '_P.args', **kwargs: '_P.kwargs') -> 'AwaitableResultWrapper[_F_default_co | _F, _S_default_co]'
>>> async def persist(s: str) -> Result[str, None]:
...     await asyncio.sleep(0.001)
...     if len(s) > 10:
...         return "failure", "out of disk space"
...     return "success", None
...
>>> awaitable_result_wrapper_1 = AwaitableResultWrapper.construct_success(
...     "short"
... ).tap_success_to_awaitable_result(persist)
>>> awaitable_result_wrapper_1
AwaitableResultWrapper(core=<coroutine object ...>)
>>> asyncio.run(awaitable_result_wrapper_1.core_as_coroutine)
('success', 'short')
>>> awaitable_result_wrapper_2 = AwaitableResultWrapper.construct_success(
...     "a very long string"
... ).tap_success_to_awaitable_result(persist)
>>> awaitable_result_wrapper_2
AwaitableResultWrapper(core=<coroutine object ...>)
>>> asyncio.run(awaitable_result_wrapper_2.core_as_coroutine)
('failure', 'out of disk space')

```

`AwaitableTupleWrapper.tap_to_awaitable`
and `AwaitableResultTupleWrapper.tap_successes_to_awaitable_result`
work analogously for tuples and success tuples.

### Unwrapping awaitable values

The attribute `core` of a `BaseAwaitableWrapper` subclass instance
has type `collections.abc.Awaitable`.
On Python versions older than 3.14,
`asyncio.run` expects a `collections.abc.Coroutine` object instead,
a subtype of `collections.abc.Awaitable`.
Use the property `core_as_coroutine`
to turn the wrapped `collections.abc.Awaitable` object
into a `collections.abc.Coroutine` object:

```pycon
>>> from collections.abc import Coroutine
>>> from typing import Any
>>> wrapped: AwaitableWrapper[int] = AwaitableWrapper.construct(42)
>>> unwrapped: Coroutine[Any, Any, int] = wrapped.core_as_coroutine
>>> unwrapped
<coroutine object ...>
>>> asyncio.run(unwrapped)
42

```

## Further reading

Check the docstrings of the classes and methods in `trcks.oop` for more
explanations and examples.
