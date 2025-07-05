"""Monadic functions for `trcks.AwaitableResult`.

Provides utilities for functional composition of
asynchronous `trcks.Result`-returning functions.

Example:
    >>> import asyncio
    >>> import math
    >>> from trcks import Result
    >>> from trcks.fp.composition import pipe
    >>> from trcks.fp.monads import awaitable_result as ar
    >>> async def read_from_disk() -> Result[str, float]:
    ...     await asyncio.sleep(0.001)
    ...     return "failure", "not found"
    ...
    >>> def get_square_root(x: float) -> Result[str, float]:
    ...     if x < 0:
    ...         return "failure", "negative value"
    ...     return "success", math.sqrt(x)
    ...
    >>> async def write_to_disk(output: float) -> None:
    ...     await asyncio.sleep(0.001)
    ...     print(f"Wrote '{output}' to disk.")
    ...
    >>> async def main() -> Result[str, float]:
    ...     awaitable_result = read_from_disk()
    ...     return await pipe(
    ...         (
    ...             awaitable_result,
    ...             ar.map_success_to_result(get_square_root),
    ...             ar.tap_success_to_awaitable(write_to_disk),
    ...         )
    ...     )
    ...
    >>> asyncio.run(main())
    ('failure', 'not found')
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from trcks._typing import TypeVar, assert_never
from trcks.fp.monads import awaitable as a
from trcks.fp.monads import result as r

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Awaitable, Callable

    from trcks import AwaitableFailure, AwaitableResult, AwaitableSuccess, Result

__docformat__ = "google"

_F = TypeVar("_F")
_F1 = TypeVar("_F1")
_F2 = TypeVar("_F2")
_S = TypeVar("_S")
_S1 = TypeVar("_S1")
_S2 = TypeVar("_S2")


def construct_failure(value: _F) -> AwaitableFailure[_F]:
    """Create an `AwaitableFailure` object from a value.

    Args:
        value: Value to be wrapped in an `AwaitableFailure` object.

    Returns:
        A new `AwaitableFailure` instance containing the given value.

    Example:
        >>> import asyncio
        >>> from collections.abc import Awaitable
        >>> from trcks.fp.monads import awaitable_result as ar
        >>> a_rslt = ar.construct_failure("not found")
        >>> isinstance(a_rslt, Awaitable)
        True
        >>> asyncio.run(ar.to_coroutine_result(a_rslt))
        ('failure', 'not found')
    """
    return a.construct(r.construct_failure(value))


def construct_failure_from_awaitable(awtbl: Awaitable[_F]) -> AwaitableFailure[_F]:
    """Create an `AwaitableFailure` object from an `Awaitable` object.

    Args:
        awtbl: `Awaitable` object to be wrapped in an `AwaitableFailure` object.

    Returns:
        A new `AwaitableFailure` instance containing
        the value of the given `Awaitable` object.

    Example:
        >>> import asyncio
        >>> from collections.abc import Awaitable
        >>> from http import HTTPStatus
        >>> from trcks.fp.monads import awaitable_result as ar
        >>> async def get_status() -> HTTPStatus:
        ...     await asyncio.sleep(0.001)
        ...     return HTTPStatus.NOT_FOUND
        ...
        >>> awaitable_status = get_status()
        >>> isinstance(awaitable_status, Awaitable)
        True
        >>> a_rslt = ar.construct_failure_from_awaitable(awaitable_status)
        >>> asyncio.run(ar.to_coroutine_result(a_rslt))
        ('failure', <HTTPStatus.NOT_FOUND: 404>)
    """
    return a.map_(r.construct_failure)(awtbl)


def construct_from_result(rslt: Result[_F, _S]) -> AwaitableResult[_F, _S]:
    """Create an `AwaitableResult` object from a `Result` object.

    Args:
        rslt: `Result` object to be wrapped in an `AwaitableResult` object.

    Returns:
        A new `AwaitableResult` instance containing
        the value of the given `Result` object.

    Example:
        >>> import asyncio
        >>> from collections.abc import Awaitable
        >>> from trcks.fp.monads import awaitable_result as ar
        >>> a_rslt = ar.construct_from_result(("failure", "not found"))
        >>> isinstance(a_rslt, Awaitable)
        True
        >>> asyncio.run(ar.to_coroutine_result(a_rslt))
        ('failure', 'not found')
    """
    return a.construct(rslt)


def construct_success(value: _S) -> AwaitableSuccess[_S]:
    """Create an `AwaitableSuccess` object from a value.

    Args:
        value: Value to be wrapped in an `AwaitableSuccess` object.

    Returns:
        A new `AwaitableSuccess` instance containing the given value.

    Example:
        >>> import asyncio
        >>> from collections.abc import Awaitable
        >>> from trcks.fp.monads import awaitable_result as ar
        >>> a_rslt = ar.construct_success(42)
        >>> isinstance(a_rslt, Awaitable)
        True
        >>> asyncio.run(ar.to_coroutine_result(a_rslt))
        ('success', 42)
    """
    return a.construct(r.construct_success(value))


def construct_success_from_awaitable(awtbl: Awaitable[_S]) -> AwaitableSuccess[_S]:
    """Create an `AwaitableSuccess` object from an `Awaitable` object.

    Args:
        awtbl: `Awaitable` object to be wrapped in an `AwaitableSuccess` object.

    Returns:
        A new `AwaitableSuccess` instance containing
        the value of the given `Awaitable` object.

    Example:
        >>> import asyncio
        >>> from collections.abc import Awaitable
        >>> from trcks.fp.monads import awaitable_result as ar
        >>> async def read_from_disk() -> str:
        ...     await asyncio.sleep(0.001)
        ...     return "Hello, world!"
        ...
        >>> awaitable_str = read_from_disk()
        >>> isinstance(awaitable_str, Awaitable)
        True
        >>> a_rslt = ar.construct_success_from_awaitable(awaitable_str)
        >>> asyncio.run(ar.to_coroutine_result(a_rslt))
        ('success', 'Hello, world!')
    """
    return a.map_(r.construct_success)(awtbl)


def map_failure(
    f: Callable[[_F1], _F2],
) -> Callable[[AwaitableResult[_F1, _S1]], AwaitableResult[_F2, _S1]]:
    """Create function that maps `AwaitableFailure` to `AwaitableFailure` values.

    `AwaitableSuccess` values are left unchanged.

    Args:
        f: Synchronous function to apply to the `AwaitableFailure` values.

    Returns:
        Maps `AwaitableFailure` values to `AwaitableFailure` values
        according to the given function and
        leaves `AwaitableSuccess` values unchanged.

    Example:
        >>> import asyncio
        >>> from trcks import AwaitableResult
        >>> from trcks.fp.monads import awaitable_result as ar
        >>> add_prefix_to_failure = ar.map_failure(lambda s: f"Prefix: {s}")
        >>> a_rslt_1: AwaitableResult[str, float] = add_prefix_to_failure(
        ...     ar.construct_failure("negative value")
        ... )
        >>> asyncio.run(ar.to_coroutine_result(a_rslt_1))
        ('failure', 'Prefix: negative value')
        >>> a_rslt_2: AwaitableResult[str, float] = add_prefix_to_failure(
        ...     ar.construct_success(25.0)
        ... )
        >>> asyncio.run(ar.to_coroutine_result(a_rslt_2))
        ('success', 25.0)
    """
    return a.map_(r.map_failure(f))


def map_failure_to_awaitable(
    f: Callable[[_F1], Awaitable[_F2]],
) -> Callable[[AwaitableResult[_F1, _S1]], AwaitableResult[_F2, _S1]]:
    """Create function that maps `AwaitableFailure` to `AwaitableFailure` values.

    `AwaitableSuccess` values are left unchanged.

    Args:
        f: Asynchronous function to apply to the `AwaitableFailure` values.

    Returns:
        Maps `AwaitableFailure` values to `AwaitableFailure` values
        according to the given asynchronous function and
        leaves `AwaitableSuccess` values unchanged.

    Example:
        >>> import asyncio
        >>> from trcks import AwaitableResult
        >>> from trcks.fp.monads import awaitable_result as ar
        >>> async def slowly_add_prefix(s: str) -> str:
        ...     await asyncio.sleep(0.001)
        ...     return f"Prefix: {s}"
        ...
        >>> slowly_add_prefix_to_failure = ar.map_failure_to_awaitable(
        ...     slowly_add_prefix
        ... )
        >>> a_rslt_1: AwaitableResult[str, float] = slowly_add_prefix_to_failure(
        ...     ar.construct_failure("negative value")
        ... )
        >>> asyncio.run(ar.to_coroutine_result(a_rslt_1))
        ('failure', 'Prefix: negative value')
        >>> a_rslt_2: AwaitableResult[str, float] = slowly_add_prefix_to_failure(
        ...     ar.construct_success(25.0)
        ... )
        >>> asyncio.run(ar.to_coroutine_result(a_rslt_2))
        ('success', 25.0)
    """

    def composed_f(value: _F1) -> AwaitableFailure[_F2]:
        return construct_failure_from_awaitable(f(value))

    return map_failure_to_awaitable_result(composed_f)


def map_failure_to_awaitable_result(
    f: Callable[[_F1], AwaitableResult[_F2, _S2]],
) -> Callable[[AwaitableResult[_F1, _S1]], AwaitableResult[_F2, _S1 | _S2]]:
    """Create function that maps `AwaitableFailure` values to `AwaitableResult` values.

    `AwaitableSuccess` values are left unchanged.

    Args:
        f: Asynchronous function to apply to the `AwaitableFailure` values.

    Returns:
        Maps `AwaitableFailure` values
        to `AwaitableFailure` and `AwaitableSuccess` values
        according to the given asynchronous function and
        leaves `AwaitableSuccess` values unchanged.

    Example:
        >>> import asyncio
        >>> from trcks import Result
        >>> from trcks.fp.monads import awaitable_result as ar
        >>> async def _slowly_replace_not_found(s: str) -> Result[str, float]:
        ...     await asyncio.sleep(0.001)
        ...     if s == "not found":
        ...         return "success", 0.0
        ...     return "failure", s
        ...
        >>> slowly_replace_not_found = ar.map_failure_to_awaitable_result(
        ...     _slowly_replace_not_found
        ... )
        >>>
        >>> a_rslt_1 = slowly_replace_not_found(ar.construct_failure("not found"))
        >>> asyncio.run(ar.to_coroutine_result(a_rslt_1))
        ('success', 0.0)
        >>> a_rslt_2 = slowly_replace_not_found(ar.construct_failure("other failure"))
        >>> asyncio.run(ar.to_coroutine_result(a_rslt_2))
        ('failure', 'other failure')
        >>> a_rslt_3 = slowly_replace_not_found(ar.construct_success(25.0))
        >>> asyncio.run(ar.to_coroutine_result(a_rslt_3))
        ('success', 25.0)
    """

    async def partially_mapped_f(rslt: Result[_F1, _S1]) -> Result[_F2, _S1 | _S2]:
        if rslt[0] == "failure":
            return await f(rslt[1])
        if rslt[0] == "success":
            return rslt
        return assert_never(rslt)  # type: ignore [unreachable]  # pragma: no cover

    return a.map_to_awaitable(partially_mapped_f)


def map_failure_to_result(
    f: Callable[[_F1], Result[_F2, _S2]],
) -> Callable[[AwaitableResult[_F1, _S1]], AwaitableResult[_F2, _S1 | _S2]]:
    """Create function that maps `AwaitableFailure` values to `AwaitableResult` values.

    `AwaitableSuccess` values are left unchanged.

    Args:
        f: Synchronous function to apply to the `AwaitableFailure` values.

    Returns:
        Maps `AwaitableFailure` values to `AwaitableResult` values
        according to the given function and
        leaves `AwaitableSuccess` values unchanged.

    Example:
        >>> import asyncio
        >>> from trcks import AwaitableResult
        >>> from trcks.fp.monads import awaitable_result as ar
        >>> replace_not_found_by_default_value = ar.map_failure_to_result(
        ...     lambda s: ("success", 0.0) if s == "not found" else ("failure", s)
        ... )
        >>> a_rslt_1: AwaitableResult[str, float] = replace_not_found_by_default_value(
        ...     ar.construct_failure("not found")
        ... )
        >>> asyncio.run(ar.to_coroutine_result(a_rslt_1))
        ('success', 0.0)
        >>> a_rslt_2: AwaitableResult[str, float] = replace_not_found_by_default_value(
        ...     ar.construct_failure("other failure")
        ... )
        >>> asyncio.run(ar.to_coroutine_result(a_rslt_2))
        ('failure', 'other failure')
        >>> a_rslt_3: AwaitableResult[str, float] = replace_not_found_by_default_value(
        ...     ar.construct_success(25.0)
        ... )
        >>> asyncio.run(ar.to_coroutine_result(a_rslt_3))
        ('success', 25.0)
    """
    return a.map_(r.map_failure_to_result(f))


def map_success(
    f: Callable[[_S1], _S2],
) -> Callable[[AwaitableResult[_F1, _S1]], AwaitableResult[_F1, _S2]]:
    """Create function that maps `AwaitableSuccess` to `AwaitableSuccess` values.

    `AwaitableFailure` values are left unchanged.

    Args:
        f: Synchronous function to apply to the `AwaitableSuccess` values.

    Returns:
        Leaves `AwaitableFailure` values unchanged and
        maps `AwaitableSuccess` values to new `AwaitableSuccess` values
        according to the given function.

    Example:
        >>> import asyncio
        >>> from trcks import AwaitableResult
        >>> from trcks.fp.monads import awaitable_result as ar
        >>> def increase(n: int) -> int:
        ...     return n + 1
        ...
        >>> increase_success = ar.map_success(increase)
        >>> a_rslt_1: AwaitableResult[str, int] = increase_success(
        ...     ar.construct_failure("not found")
        ... )
        >>> asyncio.run(ar.to_coroutine_result(a_rslt_1))
        ('failure', 'not found')
        >>> a_rslt_2: AwaitableResult[str, int] = increase_success(
        ...     ar.construct_success(42)
        ... )
        >>> asyncio.run(ar.to_coroutine_result(a_rslt_2))
        ('success', 43)
    """
    return a.map_(r.map_success(f))


def map_success_to_awaitable(
    f: Callable[[_S1], Awaitable[_S2]],
) -> Callable[[AwaitableResult[_F1, _S1]], AwaitableResult[_F1, _S2]]:
    """Create function that maps `AwaitableSuccess` to `AwaitableSuccess` values.

    `AwaitableFailure` values are left unchanged.

    Args:
        f: Asynchronous function to apply to the `AwaitableSuccess` values.

    Returns:
        Leaves `AwaitableFailure` values unchanged and
        maps `AwaitableSuccess` values to new `AwaitableSuccess` values
        according to the given function.

    Example:
        >>> import asyncio
        >>>
        >>> from trcks import AwaitableResult
        >>> from trcks.fp.monads import awaitable_result as ar
        >>>
        >>>
        >>> async def increment_slowly(n: int) -> int:
        ...     return n + 1
        ...
        >>> increase_success = ar.map_success_to_awaitable(increment_slowly)
        >>>
        >>> a_rslt_1: AwaitableResult[str, int] = increase_success(
        ...     ar.construct_failure("not found")
        ... )
        >>> asyncio.run(ar.to_coroutine_result(a_rslt_1))
        ('failure', 'not found')
        >>>
        >>> a_rslt_2: AwaitableResult[str, int] = increase_success(
        ...     ar.construct_success(42)
        ... )
        >>> asyncio.run(ar.to_coroutine_result(a_rslt_2))
        ('success', 43)
    """

    def composed_f(value: _S1) -> AwaitableSuccess[_S2]:
        return construct_success_from_awaitable(f(value))

    return map_success_to_awaitable_result(composed_f)


def map_success_to_awaitable_result(
    f: Callable[[_S1], AwaitableResult[_F2, _S2]],
) -> Callable[[AwaitableResult[_F1, _S1]], AwaitableResult[_F1 | _F2, _S2]]:
    """Create function that maps `AwaitableSuccess` values to `AwaitableResult` values.

    `AwaitableFailure` values are left unchanged.

    Args:
        f: Asynchronous function to apply to the `AwaitableSuccess` values.

    Returns:
        Leaves `AwaitableFailure` values unchanged and
        maps `AwaitableSuccess` values
        to `AwaitableFailure` and `AwaitableSuccess` values
        according to the given asynchronous function.

    Example:
        >>> import asyncio
        >>> import math
        >>> from trcks import AwaitableResult, Result
        >>> from trcks.fp.monads import awaitable_result as ar
        >>> async def _get_square_root_slowly(x: float) -> Result[str, float]:
        ...     await asyncio.sleep(0.001)
        ...     if x < 0:
        ...         return "failure", "negative value"
        ...     return "success", math.sqrt(x)
        ...
        >>> get_square_root_slowly = ar.map_success_to_awaitable_result(
        ...     _get_square_root_slowly
        ... )
        >>> a_rslt_1: AwaitableResult[str, float] = get_square_root_slowly(
        ...     ar.construct_failure("not found")
        ... )
        >>> asyncio.run(ar.to_coroutine_result(a_rslt_1))
        ('failure', 'not found')
        >>> a_rslt_2: AwaitableResult[str, float] = get_square_root_slowly(
        ...     ar.construct_success(25.0)
        ... )
        >>> asyncio.run(ar.to_coroutine_result(a_rslt_2))
        ('success', 5.0)
    """

    async def partially_mapped_f(rslt: Result[_F1, _S1]) -> Result[_F1 | _F2, _S2]:
        if rslt[0] == "failure":
            return rslt
        if rslt[0] == "success":
            return await f(rslt[1])
        return assert_never(rslt)  # type: ignore [unreachable]  # pragma: no cover

    return a.map_to_awaitable(partially_mapped_f)


def map_success_to_result(
    f: Callable[[_S1], Result[_F2, _S2]],
) -> Callable[[AwaitableResult[_F1, _S1]], AwaitableResult[_F1 | _F2, _S2]]:
    """Create function that maps `AwaitableSuccess` values to `AwaitableResult` values.

    `AwaitableFailure` values are left unchanged.

    Args:
        f: Synchronous function to apply to the `AwaitableSuccess` values.

    Returns:
        Leaves `AwaitableFailure` values unchanged and
        maps `AwaitableSuccess` values
        to `AwaitableFailure` and `AwaitableSuccess` values
        according to the given function.

    Example:
        >>> import asyncio
        >>> import math
        >>> from trcks import Result
        >>> from trcks.fp.monads import awaitable_result as ar
        >>> def _get_square_root_slowly(x: float) -> Result[str, float]:
        ...     if x < 0:
        ...         return "failure", "negative value"
        ...     return "success", math.sqrt(x)
        ...
        >>> get_square_root_slowly = ar.map_success_to_result(
        ...     _get_square_root_slowly
        ... )
        >>> a_rslt_1 = get_square_root_slowly(
        ...     ar.construct_failure("not found")
        ... )
        >>> asyncio.run(ar.to_coroutine_result(a_rslt_1))
        ('failure', 'not found')
        >>> a_rslt_2 = get_square_root_slowly(
        ...     ar.construct_success(25.0)
        ... )
        >>> asyncio.run(ar.to_coroutine_result(a_rslt_2))
        ('success', 5.0)
    """
    return a.map_(r.map_success_to_result(f))


def tap_failure(
    f: Callable[[_F1], object],
) -> Callable[[AwaitableResult[_F1, _S1]], AwaitableResult[_F1, _S1]]:
    """Create function that applies a synchronous side effect
    to `AwaitableFailure` values.

    `AwaitableSuccess` values are passed on without side effects.

    Args:
        f: Synchronous side effect to apply to the `AwaitableFailure` value.

    Returns:
        Applies the given side effect to `AwaitableFailure` values and
        returns the original `AwaitableFailure` value.
        Passes on `AwaitableSuccess` values without side effects.
    """
    return a.map_(r.tap_failure(f))


def tap_failure_to_awaitable(
    f: Callable[[_F1], Awaitable[object]],
) -> Callable[[AwaitableResult[_F1, _S1]], AwaitableResult[_F1, _S1]]:
    """Create function that applies an asynchronous side effect
    to `AwaitableFailure` values.

    `AwaitableSuccess` values are passed on without side effects.

    Args:
        f: Asynchronous side effect to apply to the `AwaitableFailure` value.

    Returns:
        Applies the given side effect to `AwaitableFailure` values and
        returns the original `AwaitableFailure` value.
        Passes on `AwaitableSuccess` values without side effects.
    """

    async def bypassed_f(value: _F1) -> _F1:
        _ = await f(value)
        return value

    return map_failure_to_awaitable(bypassed_f)


def tap_failure_to_awaitable_result(
    f: Callable[[_F1], AwaitableResult[object, _S2]],
) -> Callable[[AwaitableResult[_F1, _S1]], AwaitableResult[_F1, _S1 | _S2]]:
    """Create function that applies an asynchronous side effect
    with return type `AwaitableResult` to `AwaitableFailure` values.

    `AwaitableSuccess` values are passed on without side effects.

    Args:
        f: Asynchronous side effect to apply to the `AwaitableFailure` value.

    Returns:
        Applies the given side effect to `AwaitableFailure` values.
        If the given side effect returns an `AwaitableFailure`,
        *the original* `AwaitableFailure` value is returned.
        If the given side effect returns an `AwaitableSuccess`,
        *this* `AwaitableSuccess` is returned.
        Passes on `AwaitableSuccess` values without side effects.
    """

    async def bypassed_f(value: _F1) -> Result[_F1, _S2]:
        rslt: Result[object, _S2] = await f(value)
        if rslt[0] == "failure":
            return r.construct_failure(value)
        if rslt[0] == "success":
            return rslt
        return assert_never(rslt)  # type: ignore [unreachable]  # pragma: no cover

    return map_failure_to_awaitable_result(bypassed_f)


def tap_failure_to_result(
    f: Callable[[_F1], Result[object, _S2]],
) -> Callable[[AwaitableResult[_F1, _S1]], AwaitableResult[_F1, _S1 | _S2]]:
    """Create function that applies a synchronous side effect with return type `Result`
    to `AwaitableFailure` values.

    `AwaitableSuccess` values are passed on without side effects.

    Args:
        f: Synchronous side effect to apply to the `AwaitableFailure` value.

    Returns:
        Applies the given side effect to `AwaitableFailure` values.
        If the given side effect returns a `Failure`,
        *the original* `AwaitableFailure` value is returned.
        If the given side effect returns a `Success`, *this* `Success` is returned.
        Passes on `AwaitableSuccess` values without side effects.
    """
    return a.map_(r.tap_failure_to_result(f))


def tap_success(
    f: Callable[[_S1], object],
) -> Callable[[AwaitableResult[_F1, _S1]], AwaitableResult[_F1, _S1]]:
    """Create function that applies a synchronous side effect
    to `AwaitableSuccess` values.

    `AwaitableFailure` values are passed on without side effects.

    Args:
        f: Synchronous side effect to apply to the `AwaitableSuccess` value.

    Returns:
        Passes on `AwaitableFailure` values without side effects.
        Applies the given side effect to `AwaitableSuccess` values and
        returns the original `AwaitableSuccess` value.
    """
    return a.map_(r.tap_success(f))


def tap_success_to_awaitable(
    f: Callable[[_S1], Awaitable[object]],
) -> Callable[[AwaitableResult[_F1, _S1]], AwaitableResult[_F1, _S1]]:
    """Create function that applies an asynchronous side effect
    to `AwaitableSuccess` values.

    `AwaitableFailure` values are passed on without side effects.

    Args:
        f: Asynchronous side effect to apply to the `AwaitableSuccess` value.

    Returns:
        Passes on `AwaitableFailure` values without side effects.
        Applies the given side effect to `AwaitableSuccess` values and
        returns the original `AwaitableSuccess` value.
    """

    async def bypassed_f(value: _S1) -> _S1:
        _ = await f(value)
        return value

    return map_success_to_awaitable(bypassed_f)


def tap_success_to_awaitable_result(
    f: Callable[[_S1], AwaitableResult[_F2, object]],
) -> Callable[[AwaitableResult[_F1, _S1]], AwaitableResult[_F1 | _F2, _S1]]:
    """Create function that applies an asynchronous side effect
    with return type `AwaitableResult` to `AwaitableSuccess` values.

    `AwaitableFailure` values are passed on without side effects.

    Args:
        f: Asynchronous side effect to apply to the `AwaitableSuccess` value.

    Returns:
        Passes on `AwaitableFailure` values without side effects.
        Applies the given side effect to `AwaitableSuccess` values.
        If the given side effect returns an `AwaitableFailure`,
        *this* `AwaitableFailure` is returned.
        If the given side effect returns an `AwaitableSuccess`,
        *the original* `AwaitableSuccess` value is returned.
    """

    async def bypassed_f(value: _S1) -> Result[_F2, _S1]:
        rslt: Result[_F2, object] = await f(value)
        if rslt[0] == "failure":
            return rslt
        if rslt[0] == "success":
            return r.construct_success(value)
        return assert_never(rslt)  # type: ignore [unreachable]  # pragma: no cover

    return map_success_to_awaitable_result(bypassed_f)


def tap_success_to_result(
    f: Callable[[_S1], Result[_F2, object]],
) -> Callable[[AwaitableResult[_F1, _S1]], AwaitableResult[_F1 | _F2, _S1]]:
    """Create function that applies a synchronous side effect with return type `Result`
    to `AwaitableSuccess` values.

    `AwaitableFailure` values are passed on without side effects.

    Args:
        f: Synchronous side effect to apply to the `AwaitableSuccess` value.

    Returns:
        Passes on `AwaitableFailure` values without side effects.
        Applies the given side effect to `AwaitableSuccess` values.
        If the given side effect returns a `Failure`, *this* `Failure` is returned.
        If the given side effect returns a `Success`,
        *the original* `AwaitableSuccess` value is returned.
    """
    return a.map_(r.tap_success_to_result(f))


async def to_coroutine_result(a_rslt: AwaitableResult[_F, _S]) -> Result[_F, _S]:
    """Turn an `AwaitableResult` into a `collections.abc.Coroutine`.

    This is useful for functions that expect a coroutine (e.g. `asyncio.run`).

    Args:
        a_rslt:
            The `AwaitableResult` to be transformed into a `collections.abc.Coroutine`.

    Returns:
        The given `AwaitableResult` transformed into a `collections.abc.Coroutine`.

    Example:
        >>> import asyncio
        >>> from trcks import Result
        >>> from trcks.fp.monads import awaitable_result as ar
        >>> asyncio.set_event_loop(asyncio.new_event_loop())
        >>> future = asyncio.Future[Result[str, int]]()
        >>> future.set_result(("success", 42))
        >>> future
        <Future finished result=('success', 42)>
        >>> coro = ar.to_coroutine_result(future)
        >>> coro
        <coroutine object to_coroutine_result at ...>
        >>> asyncio.run(coro)
        ('success', 42)
    """
    return await a_rslt
