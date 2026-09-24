"""Functions for the identity monad.

Provides utilities for functional composition of synchronous functions.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Concatenate, ParamSpec

from trcks._typing import Never, TypeVar, deprecated
from trcks.fp._monads import awaitable as a
from trcks.fp._monads import awaitable_result as ar
from trcks.fp._monads import awaitable_result_tuple as art
from trcks.fp._monads import awaitable_tuple as at
from trcks.fp._monads import result as r
from trcks.fp._monads import result_tuple as rt
from trcks.fp._monads import tuple_ as t
from trcks.fp._monads.identity import tap
from trcks.fp.composition import Composable2, compose

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable, Iterable

    from trcks import (
        AwaitableIterable,
        AwaitableResult,
        AwaitableResultIterable,
        AwaitableResultTuple,
        AwaitableTuple,
        Result,
        ResultIterable,
        ResultTuple,
    )

__all__ = [
    "map_to_awaitable",
    "map_to_awaitable_iterable",
    "map_to_awaitable_result",
    "map_to_awaitable_result_iterable",
    "map_to_awaitable_result_tuple",
    "map_to_awaitable_tuple",
    "map_to_iterable",
    "map_to_result",
    "map_to_result_iterable",
    "map_to_result_tuple",
    "map_to_tuple",
    "tap",
    "tap_to_awaitable",
    "tap_to_awaitable_iterable",
    "tap_to_awaitable_result",
    "tap_to_awaitable_result_iterable",
    "tap_to_awaitable_result_tuple",
    "tap_to_awaitable_tuple",
    "tap_to_iterable",
    "tap_to_result",
    "tap_to_result_iterable",
    "tap_to_result_tuple",
    "tap_to_tuple",
]
__docformat__ = "google"

_F = TypeVar("_F")
_P = ParamSpec("_P")
_S = TypeVar("_S")
_T1 = TypeVar("_T1")
_T2 = TypeVar("_T2")


def map_to_awaitable(
    callable_: Callable[Concatenate[_T1, _P], Awaitable[_T2]],
    /,
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[_T1], Awaitable[_T2]]:
    """Create function that maps a plain value
    to an [`Awaitable`][collections.abc.Awaitable] value.

    Args:
        callable_: Asynchronous function to apply to the given value.
        *args:
            Positional arguments to be passed to `callable_`.
        **kwargs:
            Keyword arguments to be passed to `callable_`.

    Returns:
        Maps plain values to [`Awaitable`][collections.abc.Awaitable] values
            according to the given asynchronous function.

    Examples:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable as a
        >>> from trcks.fp.monads import identity as i
        >>> async def stringify_slowly(o: object) -> str:
        ...     await asyncio.sleep(0.001)
        ...     return str(o)
        ...
        >>> stringify = i.map_to_awaitable(stringify_slowly)
        >>> awtbl = stringify(3.14)
        >>> asyncio.run(a.to_coroutine(awtbl))
        '3.14'
    """
    return compose(a.construct, a.map_to_awaitable(callable_, *args, **kwargs))


def map_to_awaitable_iterable(
    callable_: Callable[Concatenate[_T1, _P], AwaitableIterable[_T2]],
    /,
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[_T1], AwaitableTuple[_T2]]:
    """Create function that maps a plain value
    to a [`AwaitableIterable`][trcks.AwaitableIterable] and flattens the result.

    Args:
        callable_: Asynchronous function to apply to the given value,
            returning a [`AwaitableIterable`][trcks.AwaitableIterable].
        *args:
            Positional arguments to be passed to `callable_`.
        **kwargs:
            Keyword arguments to be passed to `callable_`.

    Returns:
        Maps plain values to [`AwaitableTuple`][trcks.AwaitableTuple]s of varying length
            according to the given asynchronous function.

    Examples:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_tuple as at
        >>> from trcks.fp.monads import identity as i
        >>> async def slowly_duplicate(n: int) -> tuple[int, int]:
        ...     await asyncio.sleep(0.001)
        ...     return n, n
        ...
        >>> duplicate = i.map_to_awaitable_iterable(slowly_duplicate)
        >>> a_tpl = duplicate(7)
        >>> asyncio.run(at.to_coroutine_tuple(a_tpl))
        (7, 7)
    """
    return compose(
        at.construct, at.map_to_awaitable_iterable(callable_, *args, **kwargs)
    )


def map_to_awaitable_result(
    callable_: Callable[Concatenate[_T1, _P], AwaitableResult[_F, _S]],
    /,
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[_T1], AwaitableResult[_F, _S]]:
    """Create function that maps a plain value to a
    [`AwaitableResult`][trcks.AwaitableResult] value.

    Args:
        callable_: Asynchronous function to apply to the given value,
            returning a [`AwaitableResult`][trcks.AwaitableResult].
        *args:
            Positional arguments to be passed to `callable_`.
        **kwargs:
            Keyword arguments to be passed to `callable_`.

    Returns:
        Maps plain values to [`AwaitableResult`][trcks.AwaitableResult] values
            according to the given asynchronous function.

    Examples:
        >>> import asyncio
        >>> from trcks import Result
        >>> from trcks.fp.monads import awaitable_result as ar
        >>> from trcks.fp.monads import identity as i
        >>> async def slowly_assert_non_negative(
        ...     x: float,
        ... ) -> Result[str, float]:
        ...     await asyncio.sleep(0.001)
        ...     if x < 0:
        ...         return "failure", "negative value"
        ...     return "success", x
        ...
        >>> assert_non_negative = i.map_to_awaitable_result(
        ...     slowly_assert_non_negative
        ... )
        >>> a_rslt = assert_non_negative(42.0)
        >>> asyncio.run(ar.to_coroutine_result(a_rslt))
        ('success', 42.0)
    """
    c: Composable2[
        [_T1],
        AwaitableResult[Never, _T1],
        AwaitableResult[_F, _S],
    ] = (
        ar.construct_success,
        ar.map_success_to_awaitable_result(callable_, *args, **kwargs),
    )
    return compose(*c)


def map_to_awaitable_result_iterable(
    callable_: Callable[Concatenate[_T1, _P], AwaitableResultIterable[_F, _S]],
    /,
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[_T1], AwaitableResultTuple[_F, _S]]:
    """Create function that maps a plain value to a
    [`AwaitableResultIterable`][trcks.AwaitableResultIterable] and flattens the result.

    Args:
        callable_: Asynchronous function to apply to the given value,
            returning a [`AwaitableResultIterable`][trcks.AwaitableResultIterable].
        *args:
            Positional arguments to be passed to `callable_`.
        **kwargs:
            Keyword arguments to be passed to `callable_`.

    Returns:
        Maps plain values to [`AwaitableResultTuple`][trcks.AwaitableResultTuple]s with

            - the [`Failure`][trcks.Failure] returned by the function, or
            - a [`SuccessTuple`][trcks.SuccessTuple] containing the elements of
                the [`SuccessIterable`][trcks.SuccessIterable] returned by the function.

    Examples:
        >>> import asyncio
        >>> from trcks import AwaitableResultTuple
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> from trcks.fp.monads import identity as i
        >>> async def validate(x: float) -> AwaitableResultTuple[str, float]:
        ...     await asyncio.sleep(0.001)
        ...     if x < 0:
        ...         return "failure", "negative value"
        ...     return "success", (x, x * 2)
        ...
        >>> validate_value = i.map_to_awaitable_result_iterable(validate)
        >>> a_r_tpl = validate_value(5.0)
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl))
        ('success', (5.0, 10.0))
    """
    c: Composable2[
        [_T1],
        AwaitableResultTuple[Never, _T1],
        AwaitableResultTuple[_F, _S],
    ] = (
        art.construct_successes,
        art.map_successes_to_awaitable_result_iterable(callable_, *args, **kwargs),
    )
    return compose(*c)


@deprecated("Use map_to_awaitable_result_iterable instead")
def map_to_awaitable_result_tuple(
    callable_: Callable[Concatenate[_T1, _P], AwaitableResultTuple[_F, _S]],
    /,
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[_T1], AwaitableResultTuple[_F, _S]]:
    """Deprecated alias for
    [`map_to_awaitable_result_iterable`][trcks.fp.monads.identity.map_to_awaitable_result_iterable].
    """
    return map_to_awaitable_result_iterable(
        callable_, *args, **kwargs
    )  # pragma: no cover


@deprecated("Use map_to_awaitable_iterable instead")
def map_to_awaitable_tuple(
    callable_: Callable[Concatenate[_T1, _P], AwaitableTuple[_T2]],
    /,
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[_T1], AwaitableTuple[_T2]]:
    """Deprecated alias for
    [`map_to_awaitable_iterable`][trcks.fp.monads.identity.map_to_awaitable_iterable].
    """
    return map_to_awaitable_iterable(callable_, *args, **kwargs)  # pragma: no cover


def map_to_iterable(
    callable_: Callable[Concatenate[_T1, _P], Iterable[_T2]],
    /,
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[_T1], tuple[_T2, ...]]:
    """Create function that maps a plain value
    to a [`Iterable`][collections.abc.Iterable] and flattens the result.

    Args:
        callable_: Function to apply to the given value,
            returning a [`Iterable`][collections.abc.Iterable].
        *args:
            Positional arguments to be passed to `callable_`.
        **kwargs:
            Keyword arguments to be passed to `callable_`.

    Returns:
        Maps plain values to homogeneous [`tuple`][tuple]s of varying length
            according to the given function.

    Examples:
        >>> from trcks.fp.monads import identity as i
        >>> def duplicate(n: int) -> tuple[int, int]:
        ...     return n, n
        ...
        >>> duplicate_value = i.map_to_iterable(duplicate)
        >>> duplicate_value(3)
        (3, 3)
    """
    return compose(t.construct, t.map_to_iterable(callable_, *args, **kwargs))


def map_to_result(
    callable_: Callable[Concatenate[_T1, _P], Result[_F, _S]],
    /,
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[_T1], Result[_F, _S]]:
    """Create function that maps a plain value to a [`Result`][trcks.Result] value.

    Args:
        callable_: Function to apply to the given value, returning a
            [`Result`][trcks.Result].
        *args:
            Positional arguments to be passed to `callable_`.
        **kwargs:
            Keyword arguments to be passed to `callable_`.

    Returns:
        Maps plain values to [`Result`][trcks.Result] values
            according to the given function.

    Examples:
        >>> from trcks.fp.monads import identity as i
        >>> assert_non_negative = i.map_to_result(
        ...     lambda n: ("success", n)
        ...     if n >= 0
        ...     else ("failure", "negative value")
        ... )
        >>> assert_non_negative(-1)
        ('failure', 'negative value')
    """
    c: Composable2[
        [_T1],
        Result[Never, _T1],
        Result[_F, _S],
    ] = (r.construct_success, r.map_success_to_result(callable_, *args, **kwargs))
    return compose(*c)


def map_to_result_iterable(
    callable_: Callable[Concatenate[_T1, _P], ResultIterable[_F, _S]],
    /,
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[_T1], ResultTuple[_F, _S]]:
    """Create function that maps a plain value
    to a [`ResultIterable`][trcks.ResultIterable] and flattens the result.

    Args:
        callable_: Function to apply to the given value,
            returning a [`ResultIterable`][trcks.ResultIterable].
        *args:
            Positional arguments to be passed to `callable_`.
        **kwargs:
            Keyword arguments to be passed to `callable_`.

    Returns:
        Maps plain values to [`ResultTuple`][trcks.ResultTuple]s with

            - the [`Failure`][trcks.Failure] returned by the function, or
            - a [`SuccessTuple`][trcks.SuccessTuple] containing the elements of
                the [`SuccessIterable`][trcks.SuccessIterable] returned by the function.

    Examples:
        >>> from trcks.fp.monads import identity as i
        >>> duplicate_value = i.map_to_result_iterable(
        ...     lambda n: ("success", (n, n))
        ...     if n >= 0
        ...     else ("failure", "negative value")
        ... )
        >>> duplicate_value(-1)
        ('failure', 'negative value')
    """
    c: Composable2[
        [_T1],
        ResultTuple[Never, _T1],
        ResultTuple[_F, _S],
    ] = (
        rt.construct_successes,
        rt.map_successes_to_result_iterable(callable_, *args, **kwargs),
    )
    return compose(*c)


@deprecated("Use map_to_result_iterable instead")
def map_to_result_tuple(
    callable_: Callable[Concatenate[_T1, _P], ResultTuple[_F, _S]],
    /,
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[_T1], ResultTuple[_F, _S]]:
    """Deprecated alias for
    [`map_to_result_iterable`][trcks.fp.monads.identity.map_to_result_iterable].
    """
    return map_to_result_iterable(callable_, *args, **kwargs)  # pragma: no cover


@deprecated("Use map_to_iterable instead")
def map_to_tuple(
    callable_: Callable[Concatenate[_T1, _P], tuple[_T2, ...]],
    /,
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[_T1], tuple[_T2, ...]]:
    """Deprecated alias for
    [`map_to_iterable`][trcks.fp.monads.identity.map_to_iterable].
    """
    return map_to_iterable(callable_, *args, **kwargs)  # pragma: no cover


def tap_to_awaitable(
    callable_: Callable[Concatenate[_T1, _P], Awaitable[object]],
    /,
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[_T1], Awaitable[_T1]]:
    """Create function that applies an asynchronous side effect to a plain value.

    Args:
        callable_: Asynchronous side effect to apply to the given value.
        *args:
            Positional arguments to be passed to `callable_`.
        **kwargs:
            Keyword arguments to be passed to `callable_`.

    Returns:
        Applies the given side effect to the given value and
            returns an [`Awaitable`][collections.abc.Awaitable] of the original value.

    Examples:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable as a
        >>> from trcks.fp.monads import identity as i
        >>> async def write_to_disk(s: str) -> None:
        ...     await asyncio.sleep(0.001)
        ...     print(f"Wrote '{s}' to disk.")
        ...
        >>> write_to_disk_tapped = i.tap_to_awaitable(write_to_disk)
        >>> awtbl = write_to_disk_tapped("Hello, world!")
        >>> value = asyncio.run(a.to_coroutine(awtbl))
        Wrote 'Hello, world!' to disk.
        >>> value
        'Hello, world!'
    """
    return compose(a.construct, a.tap_to_awaitable(callable_, *args, **kwargs))


def tap_to_awaitable_iterable(
    callable_: Callable[Concatenate[_T1, _P], AwaitableIterable[object]],
    /,
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[_T1], AwaitableTuple[_T1]]:
    """Create function that applies an asynchronous side effect
    with return type [`AwaitableIterable`][trcks.AwaitableIterable] to a plain value.

    Args:
        callable_: Asynchronous side effect to apply to the given value,
            returning a [`AwaitableIterable`][trcks.AwaitableIterable].
        *args:
            Positional arguments to be passed to `callable_`.
        **kwargs:
            Keyword arguments to be passed to `callable_`.

    Returns:
        Applies the given side effect to the given value and
            returns a [`AwaitableTuple`][trcks.AwaitableTuple] of the original value,
            repeated once per element in the side effect output.

    Examples:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_tuple as at
        >>> from trcks.fp.monads import identity as i
        >>> async def write_to_disk(n: int) -> tuple[str, str]:
        ...     await asyncio.sleep(0.001)
        ...     print(f"Wrote {n} to disk.")
        ...     return "left", "right"
        ...
        >>> write_to_disk_tapped = i.tap_to_awaitable_iterable(write_to_disk)
        >>> a_tpl = write_to_disk_tapped(3)
        >>> asyncio.run(at.to_coroutine_tuple(a_tpl))
        Wrote 3 to disk.
        (3, 3)
    """
    return compose(
        at.construct, at.tap_to_awaitable_iterable(callable_, *args, **kwargs)
    )


def tap_to_awaitable_result(
    callable_: Callable[Concatenate[_T1, _P], AwaitableResult[_F, object]],
    /,
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[_T1], AwaitableResult[_F, _T1]]:
    """Create function that applies an asynchronous side effect
    with return type [`Result`][trcks.Result] to a plain value.

    Args:
        callable_: Asynchronous side effect to apply to the given value,
            returning a [`Result`][trcks.Result].
        *args:
            Positional arguments to be passed to `callable_`.
        **kwargs:
            Keyword arguments to be passed to `callable_`.

    Returns:
        Applies the given side effect to the given value and
            returns a [`AwaitableResult`][trcks.AwaitableResult] with

                - *the returned* [`Failure`][trcks.Failure]
                    if the applied side effect returns a [`Failure`][trcks.Failure] or
                - *the original* value
                    if the applied side effect returns a [`Success`][trcks.Success].

    Examples:
        >>> import asyncio
        >>> from trcks import Result
        >>> from trcks.fp.monads import awaitable_result as ar
        >>> from trcks.fp.monads import identity as i
        >>> async def write_to_disk(s: str, path: str) -> Result[str, None]:
        ...     if path != "output.txt":
        ...         return "failure", "write error"
        ...     await asyncio.sleep(0.001)
        ...     print(f"Wrote '{s}' to file {path}.")
        ...     return "success", None
        ...
        >>> write_to_disk_tapped = i.tap_to_awaitable_result(
        ...     lambda s: write_to_disk(s, "destination.txt")
        ... )
        >>> a_rslt_1 = write_to_disk_tapped("Hello, world!")
        >>> asyncio.run(ar.to_coroutine_result(a_rslt_1))
        ('failure', 'write error')
        >>> write_to_disk_tapped = i.tap_to_awaitable_result(
        ...     lambda s: write_to_disk(s, "output.txt")
        ... )
        >>> a_rslt_2 = write_to_disk_tapped("Hello, world!")
        >>> asyncio.run(ar.to_coroutine_result(a_rslt_2))
        Wrote 'Hello, world!' to file output.txt.
        ('success', 'Hello, world!')
    """
    c: Composable2[
        [_T1],
        AwaitableResult[Never, _T1],
        AwaitableResult[_F, _T1],
    ] = (
        ar.construct_success,
        ar.tap_success_to_awaitable_result(callable_, *args, **kwargs),
    )
    return compose(*c)


def tap_to_awaitable_result_iterable(
    callable_: Callable[Concatenate[_T1, _P], AwaitableResultIterable[_F, object]],
    /,
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[_T1], AwaitableResultTuple[_F, _T1]]:
    """Create function that applies an asynchronous side effect with return type
    [`AwaitableResultIterable`][trcks.AwaitableResultIterable] to a plain value.

    Args:
        callable_: Asynchronous side effect to apply to the given value,
            returning a [`AwaitableResultIterable`][trcks.AwaitableResultIterable].
        *args:
            Positional arguments to be passed to `callable_`.
        **kwargs:
            Keyword arguments to be passed to `callable_`.

    Returns:
        Applies the given side effect to the given value and
            returns a [`AwaitableResultTuple`][trcks.AwaitableResultTuple] with

                - *the returned* [`Failure`][trcks.Failure]
                    if the applied side effect returns a [`Failure`][trcks.Failure] or
                - *the original* value repeated once per element
                    in the side effect output if the applied side effect returns a
                    [`SuccessIterable`][trcks.SuccessIterable].

    Examples:
        >>> import asyncio
        >>> from trcks import AwaitableResultTuple
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> from trcks.fp.monads import identity as i
        >>> async def write_twice(s: str) -> AwaitableResultTuple[str, None]:
        ...     await asyncio.sleep(0.001)
        ...     print(f"Wrote '{s}' twice.")
        ...     return "success", (None, None)
        ...
        >>> write_twice_tapped = i.tap_to_awaitable_result_iterable(write_twice)
        >>> a_r_tpl = write_twice_tapped("Hello, world!")
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl))
        Wrote 'Hello, world!' twice.
        ('success', ('Hello, world!', 'Hello, world!'))
    """
    c: Composable2[
        [_T1],
        AwaitableResultTuple[Never, _T1],
        AwaitableResultTuple[_F, _T1],
    ] = (
        art.construct_successes,
        art.tap_successes_to_awaitable_result_iterable(callable_, *args, **kwargs),
    )
    return compose(*c)


@deprecated("Use tap_to_awaitable_result_iterable instead")
def tap_to_awaitable_result_tuple(
    callable_: Callable[Concatenate[_T1, _P], AwaitableResultTuple[_F, object]],
    /,
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[_T1], AwaitableResultTuple[_F, _T1]]:
    """Deprecated alias for
    [`tap_to_awaitable_result_iterable`][trcks.fp.monads.identity.tap_to_awaitable_result_iterable].
    """
    return tap_to_awaitable_result_iterable(
        callable_, *args, **kwargs
    )  # pragma: no cover


@deprecated("Use tap_to_awaitable_iterable instead")
def tap_to_awaitable_tuple(
    callable_: Callable[Concatenate[_T1, _P], AwaitableTuple[object]],
    /,
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[_T1], AwaitableTuple[_T1]]:
    """Deprecated alias for
    [`tap_to_awaitable_iterable`][trcks.fp.monads.identity.tap_to_awaitable_iterable].
    """
    return tap_to_awaitable_iterable(callable_, *args, **kwargs)  # pragma: no cover


def tap_to_iterable(
    callable_: Callable[Concatenate[_T1, _P], Iterable[object]],
    /,
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[_T1], tuple[_T1, ...]]:
    """Create function that applies a side effect
    returning a [`Iterable`][collections.abc.Iterable] to a plain value.

    Args:
        callable_: Side effect to apply to the given value,
            returning a [`Iterable`][collections.abc.Iterable].
        *args:
            Positional arguments to be passed to `callable_`.
        **kwargs:
            Keyword arguments to be passed to `callable_`.

    Returns:
        Applies the given side effect to the given value and
            returns a homogeneous [`tuple`][tuple] of the original value,
            repeated once per element in the side effect output.

    Examples:
        >>> from trcks.fp.monads import identity as i
        >>> def write_to_disk(n: int) -> tuple[str, str]:
        ...     print(f"Wrote {n} to disk.")
        ...     return "left", "right"
        ...
        >>> write_to_disk_tapped = i.tap_to_iterable(write_to_disk)
        >>> write_to_disk_tapped(3)
        Wrote 3 to disk.
        (3, 3)
    """
    return compose(t.construct, t.tap_to_iterable(callable_, *args, **kwargs))


def tap_to_result(
    callable_: Callable[Concatenate[_T1, _P], Result[_F, object]],
    /,
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[_T1], Result[_F, _T1]]:
    """Create function that applies a side effect
    with return type [`Result`][trcks.Result] to a plain value.

    Args:
        callable_: Side effect to apply to the given value,
            returning a [`Result`][trcks.Result].
        *args:
            Positional arguments to be passed to `callable_`.
        **kwargs:
            Keyword arguments to be passed to `callable_`.

    Returns:
        Applies the given side effect to the given value and
            returns a [`Result`][trcks.Result] with

                - *the returned* [`Failure`][trcks.Failure]
                    if the applied side effect returns a [`Failure`][trcks.Failure] or
                - *the original* value
                    if the applied side effect returns a [`Success`][trcks.Success].

    Examples:
        >>> from trcks import Result
        >>> from trcks.fp.monads import identity as i
        >>> def print_positive_float(x: float) -> Result[str, None]:
        ...     if x <= 0:
        ...         return "failure", "not positive"
        ...     return "success", print(f"Positive float: {x}")
        ...
        >>> print_positive_float_tapped = i.tap_to_result(print_positive_float)
        >>> print_positive_float_tapped(-2.3)
        ('failure', 'not positive')
        >>> print_positive_float_tapped(3.5)
        Positive float: 3.5
        ('success', 3.5)
    """
    c: Composable2[
        [_T1],
        Result[Never, _T1],
        Result[_F, _T1],
    ] = (r.construct_success, r.tap_success_to_result(callable_, *args, **kwargs))
    return compose(*c)


def tap_to_result_iterable(
    callable_: Callable[Concatenate[_T1, _P], ResultIterable[_F, object]],
    /,
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[_T1], ResultTuple[_F, _T1]]:
    """Create function that applies a side effect
    with return type [`ResultIterable`][trcks.ResultIterable] to a plain value.

    Args:
        callable_: Side effect to apply to the given value,
            returning a [`ResultIterable`][trcks.ResultIterable].
        *args:
            Positional arguments to be passed to `callable_`.
        **kwargs:
            Keyword arguments to be passed to `callable_`.

    Returns:
        Applies the given side effect to the given value and
            returns a [`ResultTuple`][trcks.ResultTuple] with

                - *the returned* [`Failure`][trcks.Failure]
                    if the applied side effect returns a [`Failure`][trcks.Failure] or
                - *the original* value repeated once per element
                    in the side effect output if the applied side effect returns a
                    [`SuccessIterable`][trcks.SuccessIterable].

    Examples:
        >>> from trcks import ResultTuple
        >>> from trcks.fp.monads import identity as i
        >>> def print_positive_float(x: float) -> ResultTuple[str, None]:
        ...     if x <= 0:
        ...         return "failure", "not positive"
        ...     return (
        ...         "success",
        ...         (print(f"Positive float: {x}"), print(f"Positive float: {x}"))
        ...     )
        ...
        >>> print_positive_float_tapped = i.tap_to_result_iterable(
        ...     print_positive_float
        ... )
        >>> print_positive_float_tapped(-2.3)
        ('failure', 'not positive')
        >>> print_positive_float_tapped(3.5)
        Positive float: 3.5
        Positive float: 3.5
        ('success', (3.5, 3.5))
    """
    c: Composable2[
        [_T1],
        ResultTuple[Never, _T1],
        ResultTuple[_F, _T1],
    ] = (
        rt.construct_successes,
        rt.tap_successes_to_result_iterable(callable_, *args, **kwargs),
    )
    return compose(*c)


@deprecated("Use tap_to_result_iterable instead")
def tap_to_result_tuple(
    callable_: Callable[Concatenate[_T1, _P], ResultTuple[_F, object]],
    /,
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[_T1], ResultTuple[_F, _T1]]:
    """Deprecated alias for
    [`tap_to_result_iterable`][trcks.fp.monads.identity.tap_to_result_iterable].
    """
    return tap_to_result_iterable(callable_, *args, **kwargs)  # pragma: no cover


@deprecated("Use tap_to_iterable instead")
def tap_to_tuple(
    callable_: Callable[Concatenate[_T1, _P], tuple[object, ...]],
    /,
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[_T1], tuple[_T1, ...]]:
    """Deprecated alias for
    [`tap_to_iterable`][trcks.fp.monads.identity.tap_to_iterable].
    """
    return tap_to_iterable(callable_, *args, **kwargs)  # pragma: no cover
