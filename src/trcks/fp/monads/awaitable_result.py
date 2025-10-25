"""Monadic functions for [trcks.AwaitableResult][].

Provides utilities for functional composition of
asynchronous [trcks.Result][]-returning functions.

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
from trcks.fp.composition import compose2
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
    """Create a [trcks.AwaitableFailure][] object from a value.

    Args:
        value: Value to be wrapped in a [trcks.AwaitableFailure][] object.

    Returns:
        A new [trcks.AwaitableFailure][] instance containing the given value.

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
    """Create a [trcks.AwaitableFailure][] object
    from a [collections.abc.Awaitable][] object.

    Args:
        awtbl: [collections.abc.Awaitable][] object to be wrapped
            in a [trcks.AwaitableFailure][] object.

    Returns:
        A new [trcks.AwaitableFailure][] instance containing
            the value of the given [collections.abc.Awaitable][] object.

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
    """Create a [trcks.AwaitableResult][] object from a [trcks.Result][] object.

    Args:
        rslt: [trcks.Result][] object to be wrapped
            in a [trcks.AwaitableResult][] object.

    Returns:
        A new [trcks.AwaitableResult][] instance containing
            the value of the given [trcks.Result][] object.

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
    """Create a [trcks.AwaitableSuccess][] object from a value.

    Args:
        value: Value to be wrapped in a [trcks.AwaitableSuccess][] object.

    Returns:
        A new [trcks.AwaitableSuccess][] instance containing the given value.

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
    """Create a [trcks.AwaitableSuccess][] object
    from a [collections.abc.Awaitable][] object.

    Args:
        awtbl: [collections.abc.Awaitable][] object to be wrapped
            in a [trcks.AwaitableSuccess][] object.

    Returns:
        A new [trcks.AwaitableSuccess][] instance containing
            the value of the given [collections.abc.Awaitable][] object.

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
    """Create function that maps [trcks.AwaitableFailure][]
    to [trcks.AwaitableFailure][] values.

    [trcks.AwaitableSuccess][] values are left unchanged.

    Args:
        f: Synchronous function to apply to the [trcks.AwaitableFailure][] values.

    Returns:
        Maps [trcks.AwaitableFailure][] values to [trcks.AwaitableFailure][] values
            according to the given function and
            leaves [trcks.AwaitableSuccess][] values unchanged.

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
    """Create function that maps [trcks.AwaitableFailure][]
    to [trcks.AwaitableFailure][] values.

    [trcks.AwaitableSuccess][] values are left unchanged.

    Args:
        f: Asynchronous function to apply to the [trcks.AwaitableFailure][] values.

    Returns:
        Maps [trcks.AwaitableFailure][] values to [trcks.AwaitableFailure][] values
            according to the given asynchronous function and
            leaves [trcks.AwaitableSuccess][] values unchanged.

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
    return map_failure_to_awaitable_result(
        compose2((f, construct_failure_from_awaitable))
    )


def map_failure_to_awaitable_result(
    f: Callable[[_F1], AwaitableResult[_F2, _S2]],
) -> Callable[[AwaitableResult[_F1, _S1]], AwaitableResult[_F2, _S1 | _S2]]:
    """Create function that maps [trcks.AwaitableFailure][] values
    to [trcks.AwaitableResult][] values.

    [trcks.AwaitableSuccess][] values are left unchanged.

    Args:
        f: Asynchronous function to apply to the [trcks.AwaitableFailure][] values.

    Returns:
        Maps [trcks.AwaitableFailure][] values
            to [trcks.AwaitableFailure][] and [trcks.AwaitableSuccess][] values
            according to the given asynchronous function and
            leaves [trcks.AwaitableSuccess][] values unchanged.

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
        match rslt[0]:
            case "failure":
                return await f(rslt[1])
            case "success":
                return rslt
            case _:  # pragma: no cover
                return assert_never(rslt)  # type: ignore [unreachable]

    return a.map_to_awaitable(partially_mapped_f)


def map_failure_to_result(
    f: Callable[[_F1], Result[_F2, _S2]],
) -> Callable[[AwaitableResult[_F1, _S1]], AwaitableResult[_F2, _S1 | _S2]]:
    """Create function that maps [trcks.AwaitableFailure][] values
    to [trcks.AwaitableResult][] values.

    [trcks.AwaitableSuccess][] values are left unchanged.

    Args:
        f: Synchronous function to apply to the [trcks.AwaitableFailure][] values.

    Returns:
        Maps [trcks.AwaitableFailure][] values to [trcks.AwaitableResult][] values
            according to the given function and
            leaves [trcks.AwaitableSuccess][] values unchanged.

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
    """Create function that maps [trcks.AwaitableSuccess][]
    to [trcks.AwaitableSuccess][] values.

    [trcks.AwaitableFailure][] values are left unchanged.

    Args:
        f: Synchronous function to apply to the [trcks.AwaitableSuccess][] values.

    Returns:
        Leaves [trcks.AwaitableFailure][] values unchanged and
            maps [trcks.AwaitableSuccess][] values
            to new [trcks.AwaitableSuccess][] values
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
    """Create function that maps [trcks.AwaitableSuccess][]
    to [trcks.AwaitableSuccess][] values.

    [trcks.AwaitableFailure][] values are left unchanged.

    Args:
        f: Asynchronous function to apply to the [trcks.AwaitableSuccess][] values.

    Returns:
        Leaves [trcks.AwaitableFailure][] values unchanged and
            maps [trcks.AwaitableSuccess][] values
            to new [trcks.AwaitableSuccess][] values
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
    return map_success_to_awaitable_result(
        compose2((f, construct_success_from_awaitable))
    )


def map_success_to_awaitable_result(
    f: Callable[[_S1], AwaitableResult[_F2, _S2]],
) -> Callable[[AwaitableResult[_F1, _S1]], AwaitableResult[_F1 | _F2, _S2]]:
    """Create function that maps [trcks.AwaitableSuccess][] values
    to [trcks.AwaitableResult][] values.

    [trcks.AwaitableFailure][] values are left unchanged.

    Args:
        f: Asynchronous function to apply to the [trcks.AwaitableSuccess][] values.

    Returns:
        Leaves [trcks.AwaitableFailure][] values unchanged and
            maps [trcks.AwaitableSuccess][] values
            to [trcks.AwaitableFailure][] and [trcks.AwaitableSuccess][] values
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
        match rslt[0]:
            case "failure":
                return rslt
            case "success":
                return await f(rslt[1])
            case _:  # pragma: no cover
                return assert_never(rslt)  # type: ignore [unreachable]

    return a.map_to_awaitable(partially_mapped_f)


def map_success_to_result(
    f: Callable[[_S1], Result[_F2, _S2]],
) -> Callable[[AwaitableResult[_F1, _S1]], AwaitableResult[_F1 | _F2, _S2]]:
    """Create function that maps [trcks.AwaitableSuccess][] values
    to [trcks.AwaitableResult][] values.

    [trcks.AwaitableFailure][] values are left unchanged.

    Args:
        f: Synchronous function to apply to the [trcks.AwaitableSuccess][] values.

    Returns:
        Leaves [trcks.AwaitableFailure][] values unchanged and
            maps [trcks.AwaitableSuccess][] values
            to [trcks.AwaitableFailure][] and [trcks.AwaitableSuccess][] values
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
    to [trcks.AwaitableFailure][] values.

    [trcks.AwaitableSuccess][] values are passed on without side effects.

    Args:
        f: Synchronous side effect to apply to the [trcks.AwaitableFailure][] value.

    Returns:
        Applies the given side effect to [trcks.AwaitableFailure][] values and
            returns the original [trcks.AwaitableFailure][] value.
            Passes on [trcks.AwaitableSuccess][] values without side effects.
    """
    return a.map_(r.tap_failure(f))


def tap_failure_to_awaitable(
    f: Callable[[_F1], Awaitable[object]],
) -> Callable[[AwaitableResult[_F1, _S1]], AwaitableResult[_F1, _S1]]:
    """Create function that applies an asynchronous side effect
    to [trcks.AwaitableFailure][] values.

    [trcks.AwaitableSuccess][] values are passed on without side effects.

    Args:
        f: Asynchronous side effect to apply to the [trcks.AwaitableFailure][] value.

    Returns:
        Applies the given side effect to [trcks.AwaitableFailure][] values and
            returns the original [trcks.AwaitableFailure][] value.
            Passes on [trcks.AwaitableSuccess][] values without side effects.
    """

    async def bypassed_f(value: _F1) -> _F1:
        _ = await f(value)
        return value

    return map_failure_to_awaitable(bypassed_f)


def tap_failure_to_awaitable_result(
    f: Callable[[_F1], AwaitableResult[object, _S2]],
) -> Callable[[AwaitableResult[_F1, _S1]], AwaitableResult[_F1, _S1 | _S2]]:
    """Create function that applies an asynchronous side effect
    with return type [trcks.AwaitableResult][] to [trcks.AwaitableFailure][] values.

    [trcks.AwaitableSuccess][] values are passed on without side effects.

    Args:
        f: Asynchronous side effect to apply to the [trcks.AwaitableFailure][] value.

    Returns:
        Applies the given side effect to [trcks.AwaitableFailure][] values.
            If the given side effect returns a [trcks.AwaitableFailure][],
            *the original* [trcks.AwaitableFailure][] value is returned.
            If the given side effect returns a [trcks.AwaitableSuccess][],
            *this* [trcks.AwaitableSuccess][] is returned.
            Passes on [trcks.AwaitableSuccess][] values without side effects.
    """

    async def bypassed_f(value: _F1) -> Result[_F1, _S2]:
        rslt: Result[object, _S2] = await f(value)
        match rslt[0]:
            case "failure":
                return r.construct_failure(value)
            case "success":
                return rslt
            case _:  # pragma: no cover
                return assert_never(rslt)  # type: ignore [unreachable]

    return map_failure_to_awaitable_result(bypassed_f)


def tap_failure_to_result(
    f: Callable[[_F1], Result[object, _S2]],
) -> Callable[[AwaitableResult[_F1, _S1]], AwaitableResult[_F1, _S1 | _S2]]:
    """Create function that applies a synchronous side effect
    with return type [trcks.Result][] to [trcks.AwaitableFailure][] values.

    [trcks.AwaitableSuccess][] values are passed on without side effects.

    Args:
        f: Synchronous side effect to apply to the [trcks.AwaitableFailure][] value.

    Returns:
        Applies the given side effect to [trcks.AwaitableFailure][] values.
            If the given side effect returns a [trcks.Failure][],
            *the original* [trcks.AwaitableFailure][] value is returned.
            If the given side effect returns a [trcks.Success][],
            *this* [trcks.Success][] is returned.
            Passes on [trcks.AwaitableSuccess][] values without side effects.
    """
    return a.map_(r.tap_failure_to_result(f))


def tap_success(
    f: Callable[[_S1], object],
) -> Callable[[AwaitableResult[_F1, _S1]], AwaitableResult[_F1, _S1]]:
    """Create function that applies a synchronous side effect
    to [trcks.AwaitableSuccess][] values.

    [trcks.AwaitableFailure][] values are passed on without side effects.

    Args:
        f: Synchronous side effect to apply to the [trcks.AwaitableSuccess][] value.

    Returns:
        Passes on [trcks.AwaitableFailure][] values without side effects.
            Applies the given side effect to [trcks.AwaitableSuccess][] values and
            returns the original [trcks.AwaitableSuccess][] value.
    """
    return a.map_(r.tap_success(f))


def tap_success_to_awaitable(
    f: Callable[[_S1], Awaitable[object]],
) -> Callable[[AwaitableResult[_F1, _S1]], AwaitableResult[_F1, _S1]]:
    """Create function that applies an asynchronous side effect
    to [trcks.AwaitableSuccess][] values.

    [trcks.AwaitableFailure][] values are passed on without side effects.

    Args:
        f: Asynchronous side effect to apply to the [trcks.AwaitableSuccess][] value.

    Returns:
        Passes on [trcks.AwaitableFailure][] values without side effects.
            Applies the given side effect to [trcks.AwaitableSuccess][] values and
            returns the original [trcks.AwaitableSuccess][] value.
    """

    async def bypassed_f(value: _S1) -> _S1:
        _ = await f(value)
        return value

    return map_success_to_awaitable(bypassed_f)


def tap_success_to_awaitable_result(
    f: Callable[[_S1], AwaitableResult[_F2, object]],
) -> Callable[[AwaitableResult[_F1, _S1]], AwaitableResult[_F1 | _F2, _S1]]:
    """Create function that applies an asynchronous side effect
    with return type [trcks.AwaitableResult][] to [trcks.AwaitableSuccess][] values.

    [trcks.AwaitableFailure][] values are passed on without side effects.

    Args:
        f: Asynchronous side effect to apply to the [trcks.AwaitableSuccess][] value.

    Returns:
        Passes on [trcks.AwaitableFailure][] values without side effects.
            Applies the given side effect to [trcks.AwaitableSuccess][] values.
            If the given side effect returns a [trcks.AwaitableFailure][],
            *this* [trcks.AwaitableFailure][] is returned.
            If the given side effect returns a [trcks.AwaitableSuccess][],
            *the original* [trcks.AwaitableSuccess][] value is returned.
    """

    async def bypassed_f(value: _S1) -> Result[_F2, _S1]:
        rslt: Result[_F2, object] = await f(value)
        match rslt[0]:
            case "failure":
                return rslt
            case "success":
                return r.construct_success(value)
            case _:  # pragma: no cover
                return assert_never(rslt)  # type: ignore [unreachable]

    return map_success_to_awaitable_result(bypassed_f)


def tap_success_to_result(
    f: Callable[[_S1], Result[_F2, object]],
) -> Callable[[AwaitableResult[_F1, _S1]], AwaitableResult[_F1 | _F2, _S1]]:
    """Create function that applies a synchronous side effect
    with return type [trcks.Result][] to [trcks.AwaitableSuccess][] values.

    [trcks.AwaitableFailure][] values are passed on without side effects.

    Args:
        f: Synchronous side effect to apply to the [trcks.AwaitableSuccess][] value.

    Returns:
        Passes on [trcks.AwaitableFailure][] values without side effects.
            Applies the given side effect to [trcks.AwaitableSuccess][] values.
            If the given side effect returns a [trcks.Failure][],
            *this* [trcks.Failure][] is returned.
            If the given side effect returns a [trcks.Success][],
            *the original* [trcks.AwaitableSuccess][] value is returned.
    """
    return a.map_(r.tap_success_to_result(f))


async def to_coroutine_result(a_rslt: AwaitableResult[_F, _S]) -> Result[_F, _S]:
    """Turn a [trcks.AwaitableResult][] into a [collections.abc.Coroutine][].

    This is useful for functions that expect a coroutine (e.g. [asyncio.run][]).

    Args:
        a_rslt:
            The [trcks.AwaitableResult][] to be transformed
                into a [collections.abc.Coroutine][].

    Returns:
        The given [trcks.AwaitableResult][] transformed
            into a [collections.abc.Coroutine][].

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
