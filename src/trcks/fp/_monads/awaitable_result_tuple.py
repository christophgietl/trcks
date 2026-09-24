from __future__ import annotations

from typing import TYPE_CHECKING, Concatenate, ParamSpec

from trcks._typing import Never, TypeVar, assert_type
from trcks.fp._monads import awaitable as a
from trcks.fp._monads import result as r
from trcks.fp._monads import result_tuple as rt
from trcks.fp.composition import compose

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable, Iterable

    from trcks import (
        AwaitableFailure,
        AwaitableIterable,
        AwaitableResult,
        AwaitableResultIterable,
        AwaitableResultTuple,
        AwaitableSuccessTuple,
        Result,
        ResultIterable,
        ResultTuple,
        SuccessTuple,
    )

__docformat__ = "google"

_F = TypeVar("_F")
_F1 = TypeVar("_F1")
_F2 = TypeVar("_F2")
_P = ParamSpec("_P")
_S = TypeVar("_S")
_S1 = TypeVar("_S1")
_S2 = TypeVar("_S2")


def construct_failure(value: _F, /) -> AwaitableFailure[_F]:
    """Create an [`AwaitableFailure`][trcks.AwaitableFailure] object from a value.

    Args:
        value: Value to be wrapped in an [`AwaitableFailure`][trcks.AwaitableFailure]
            object.

    Returns:
        A new [`AwaitableFailure`][trcks.AwaitableFailure] instance containing the given
        value.

    Note:
        This function is equivalent to
            [`construct_failure`][trcks.fp.monads.awaitable_result.construct_failure].

    Examples:
        >>> import asyncio
        >>> from collections.abc import Awaitable
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> a_r_tpl = art.construct_failure("not found")
        >>> isinstance(a_r_tpl, Awaitable)
        True
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl))
        ('failure', 'not found')
    """
    return a.construct(rt.construct_failure(value))


def construct_failure_from_awaitable(awtbl: Awaitable[_F], /) -> AwaitableFailure[_F]:
    """Create an [`AwaitableFailure`][trcks.AwaitableFailure] object
    from an [`Awaitable`][collections.abc.Awaitable] object.

    Args:
        awtbl: [`Awaitable`][collections.abc.Awaitable] object to be wrapped
            in an [`AwaitableFailure`][trcks.AwaitableFailure] object.

    Returns:
        A new [`AwaitableFailure`][trcks.AwaitableFailure] instance containing
            the value of the given [`Awaitable`][collections.abc.Awaitable] object.

    Examples:
        >>> import asyncio
        >>> from collections.abc import Awaitable
        >>> from trcks.fp.monads import awaitable as a
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> awtbl = a.construct("not found")
        >>> a_r_tpl = art.construct_failure_from_awaitable(awtbl)
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl))
        ('failure', 'not found')
    """
    return a.map_(rt.construct_failure)(awtbl)


def construct_from_awaitable_result(
    a_rslt: AwaitableResult[_F, _S],
    /,
) -> AwaitableResultTuple[_F, _S]:
    """Create an [`AwaitableResultTuple`][trcks.AwaitableResultTuple] object
    from an [`AwaitableResult`][trcks.AwaitableResult] object.

    The success payload is wrapped in a single-element tuple.

    Args:
        a_rslt: [`AwaitableResult`][trcks.AwaitableResult] object to be converted.

    Returns:
        A new [`AwaitableResultTuple`][trcks.AwaitableResultTuple] instance where
            the success payload is wrapped in a single-element tuple,
            or the original failure is preserved.

    Examples:
        >>> import asyncio
        >>> from collections.abc import Awaitable
        >>> from trcks.fp.monads import awaitable_result as ar
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> a_rslt_1 = ar.construct_success(7)
        >>> a_r_tpl_1 = art.construct_from_awaitable_result(a_rslt_1)
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('success', (7,))
        >>> a_rslt_2 = ar.construct_failure("oops")
        >>> a_r_tpl_2 = art.construct_from_awaitable_result(a_rslt_2)
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('failure', 'oops')
    """
    return a.map_(rt.construct_from_result)(a_rslt)


def construct_from_awaitable_result_iterable(
    a_r_it: AwaitableResultIterable[_F, _S],
    /,
) -> AwaitableResultTuple[_F, _S]:
    """Create an [`AwaitableResultTuple`][trcks.AwaitableResultTuple] object
    from an [`AwaitableResultIterable`][trcks.AwaitableResultIterable] object.

    Args:
        a_r_it: [`AwaitableResultIterable`][trcks.AwaitableResultIterable] object to be
            converted.

    Returns:
        A new [`AwaitableResultTuple`][trcks.AwaitableResultTuple] instance where
            the success payload is converted to a tuple,
            or the original failure is preserved.

    Examples:
        >>> import asyncio
        >>> from trcks import ResultIterable
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> async def slowly_read_from_disk() -> ResultIterable[str, int]:
        ...     await asyncio.sleep(0.001)
        ...     return "success", [1, 2]
        ...
        >>> a_r_tpl = art.construct_from_awaitable_result_iterable(
        ...     slowly_read_from_disk()
        ... )
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl))
        ('success', (1, 2))
    """
    return a.map_(rt.construct_from_result_iterable)(a_r_it)


def construct_from_result(rslt: Result[_F, _S], /) -> AwaitableResultTuple[_F, _S]:
    """Create an [`AwaitableResultTuple`][trcks.AwaitableResultTuple] object from a
    [`Result`][trcks.Result].

    The success payload is wrapped in a single-element tuple.

    Args:
        rslt: [`Result`][trcks.Result] object to be converted.

    Returns:
        A new [`AwaitableResultTuple`][trcks.AwaitableResultTuple] instance where
            the success payload is wrapped in a single-element tuple,
            or the original failure is preserved.

    Examples:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> a_r_tpl_1 = art.construct_from_result(("success", 7))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('success', (7,))
        >>> a_r_tpl_2 = art.construct_from_result(("failure", "oops"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('failure', 'oops')
    """
    return a.construct(rt.construct_from_result(rslt))


def construct_from_result_iterable(
    r_it: ResultIterable[_F, _S],
    /,
) -> AwaitableResultTuple[_F, _S]:
    """Create an [`AwaitableResultTuple`][trcks.AwaitableResultTuple] object
    from a [`ResultIterable`][trcks.ResultIterable] object.

    Args:
        r_it: [`ResultIterable`][trcks.ResultIterable] object to be converted to a
            [`ResultTuple`][trcks.ResultTuple] and wrapped in an
            [`AwaitableResultTuple`][trcks.AwaitableResultTuple] object.

    Returns:
        A new [`AwaitableResultTuple`][trcks.AwaitableResultTuple] instance containing
            the elements of the given [`ResultIterable`][trcks.ResultIterable] object.

    Examples:
        >>> import asyncio
        >>> from collections.abc import Awaitable
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> a_r_tpl = art.construct_from_result_iterable(("success", (1, 2)))
        >>> isinstance(a_r_tpl, Awaitable)
        True
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl))
        ('success', (1, 2))
    """
    return a.construct(rt.construct_from_result_iterable(r_it))


def construct_successes(value: _S, /) -> AwaitableSuccessTuple[_S]:
    """Create an [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple] object from a
    single value.

    Args:
        value: A single value.

    Returns:
        A new [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple] instance containing
            the single value in a tuple.

    Examples:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> a_r_tpl = art.construct_successes(42)
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl))
        ('success', (42,))
    """
    return a.construct(rt.construct_successes(value))


def construct_successes_from_awaitable(
    awtbl: Awaitable[_S],
    /,
) -> AwaitableSuccessTuple[_S]:
    """Create an [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple] object
    from an [`Awaitable`][collections.abc.Awaitable] object.

    The value of the awaitable is wrapped in a single-element success tuple.

    Args:
        awtbl: [`Awaitable`][collections.abc.Awaitable] object whose resolved value
            will be wrapped in an
            [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple].

    Returns:
        A new [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple] instance containing
            the value of the given [`Awaitable`][collections.abc.Awaitable] in a tuple.

    Examples:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable as a
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> awtbl = a.construct(7)
        >>> a_r_tpl = art.construct_successes_from_awaitable(awtbl)
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl))
        ('success', (7,))
    """
    return a.map_(rt.construct_successes)(awtbl)


def construct_successes_from_awaitable_iterable(
    a_it: AwaitableIterable[_S],
    /,
) -> AwaitableSuccessTuple[_S]:
    """Create an [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple] object
    from an [`AwaitableIterable`][trcks.AwaitableIterable] object.

    Args:
        a_it: [`AwaitableIterable`][trcks.AwaitableIterable] object to be converted.

    Returns:
        A new [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple] instance containing
            the elements of the given [`AwaitableIterable`][trcks.AwaitableIterable]
            object.

    Examples:
        >>> import asyncio
        >>> from trcks import AwaitableIterable
        >>> from trcks.fp.monads import awaitable as a
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> a_it: AwaitableIterable[int] = a.construct([1, 2])
        >>> a_r_tpl = art.construct_successes_from_awaitable_iterable(a_it)
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl))
        ('success', (1, 2))
    """
    return a.map_(rt.construct_successes_from_iterable)(a_it)


def construct_successes_from_iterable(
    it: Iterable[_S],
    /,
) -> AwaitableSuccessTuple[_S]:
    """Create an [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple] object from an
    iterable.

    Args:
        it: The iterable to create
            the [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple] from.

    Returns:
        The [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple] created from the
        iterable.

    Examples:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> a_r_tpl = art.construct_successes_from_iterable((1, 2))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl))
        ('success', (1, 2))
    """
    return a.construct(rt.construct_successes_from_iterable(it))


def map_failure(
    callable_: Callable[Concatenate[_F1, _P], _F2],
    /,
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[AwaitableResultTuple[_F1, _S1]], AwaitableResultTuple[_F2, _S1]]:
    """Create function that maps [`AwaitableFailure`][trcks.AwaitableFailure]
    to [`AwaitableFailure`][trcks.AwaitableFailure] values.

    [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple] values are left unchanged.

    Args:
        callable_: Synchronous function to apply to
            [`AwaitableFailure`][trcks.AwaitableFailure] values.
        *args:
            Positional arguments to be passed to `callable_`.
        **kwargs:
            Keyword arguments to be passed to `callable_`.

    Returns:
        Maps [`AwaitableFailure`][trcks.AwaitableFailure] values to
            [`AwaitableFailure`][trcks.AwaitableFailure] values
            according to the given function and leaves
            [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple] values unchanged.

    Examples:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> def _add_prefix(description: str) -> str:
        ...     return f"err: {description}"
        ...
        >>> add_prefix = art.map_failure(_add_prefix)
        >>> a_r_tpl_1 = add_prefix(art.construct_failure("not found"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('failure', 'err: not found')
        >>> a_r_tpl_2 = add_prefix(art.construct_successes_from_iterable((1, 2)))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('success', (1, 2))
    """
    return a.map_(rt.map_failure(callable_, *args, **kwargs))


def map_failure_to_awaitable(
    callable_: Callable[Concatenate[_F1, _P], Awaitable[_F2]],
    /,
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[AwaitableResultTuple[_F1, _S1]], AwaitableResultTuple[_F2, _S1]]:
    """Create function that maps [`AwaitableFailure`][trcks.AwaitableFailure]
    to [`AwaitableFailure`][trcks.AwaitableFailure] values.

    [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple] values are left unchanged.

    Args:
        callable_: Asynchronous function to apply to
            [`AwaitableFailure`][trcks.AwaitableFailure] values.
        *args:
            Positional arguments to be passed to `callable_`.
        **kwargs:
            Keyword arguments to be passed to `callable_`.

    Returns:
        Maps [`AwaitableFailure`][trcks.AwaitableFailure] values to
            [`AwaitableFailure`][trcks.AwaitableFailure] values
            according to the given asynchronous function and leaves
            [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple] values unchanged.

    Examples:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> async def _slowly_add_prefix(s: str) -> str:
        ...     await asyncio.sleep(0.001)
        ...     return f"err: {s}"
        ...
        >>> slowly_add_prefix = art.map_failure_to_awaitable(_slowly_add_prefix)
        >>> a_r_tpl_1 = slowly_add_prefix(art.construct_failure("not found"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('failure', 'err: not found')
        >>> a_r_tpl_2 = slowly_add_prefix(
        ...     art.construct_successes_from_iterable((1, 2))
        ... )
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('success', (1, 2))
    """
    return map_failure_to_awaitable_result_iterable(
        compose(callable_, construct_failure_from_awaitable), *args, **kwargs
    )


def map_failure_to_awaitable_iterable(
    callable_: Callable[Concatenate[_F1, _P], AwaitableIterable[_S2]],
    /,
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[
    [AwaitableResultTuple[_F1, _S1]],
    Awaitable[SuccessTuple[_S1] | SuccessTuple[_S2]],
]:
    """Create function that maps [`AwaitableFailure`][trcks.AwaitableFailure] values
    to awaitable [`Iterable`][collections.abc.Iterable]s.

    [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple] values are left unchanged.

    Args:
        callable_: Asynchronous function to apply to
            [`AwaitableFailure`][trcks.AwaitableFailure] values.
        *args:
            Positional arguments to be passed to `callable_`.
        **kwargs:
            Keyword arguments to be passed to `callable_`.

    Returns:
        Maps [`AwaitableFailure`][trcks.AwaitableFailure] values to
            [`Iterable`][collections.abc.Iterable]s
            wrapped in [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple] values
            according to the given asynchronous function and leaves
            [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple] values unchanged.

    Examples:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> async def _slowly_recover_from_failure(
        ...     description: str,
        ... ) -> list[int]:
        ...     await asyncio.sleep(0.001)
        ...     if description == "not found":
        ...         return [0]
        ...     return []
        ...
        >>> slowly_recover_from_failure = art.map_failure_to_awaitable_iterable(
        ...     _slowly_recover_from_failure
        ... )
        >>> a_r_tpl_1 = slowly_recover_from_failure(
        ...     art.construct_failure("not found")
        ... )
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('success', (0,))
        >>> a_r_tpl_2 = slowly_recover_from_failure(art.construct_failure("fatal"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('success', ())
        >>> a_r_tpl_3 = slowly_recover_from_failure(
        ...     art.construct_successes_from_iterable((1, 2))
        ... )
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_3))
        ('success', (1, 2))
    """

    async def mapped_callable(
        r_tpl: ResultTuple[_F1, _S1],
    ) -> SuccessTuple[_S1] | SuccessTuple[_S2]:
        match r_tpl:
            case ("failure", value):
                return "success", tuple(await callable_(value, *args, **kwargs))
            case ("success", _):
                return r_tpl
            case _:  # pragma: no cover
                assert_type(r_tpl, Never)  # type: ignore[unreachable]  # pyright: ignore[reportUnreachable]
                msg = f"{type(r_tpl).__name__!r} is not a valid ResultTuple"
                raise TypeError(msg)

    return a.map_to_awaitable(mapped_callable)


def map_failure_to_awaitable_result(
    callable_: Callable[Concatenate[_F1, _P], AwaitableResult[_F2, _S2]],
    /,
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[
    [AwaitableResultTuple[_F1, _S1]],
    AwaitableResultTuple[_F2, _S1 | _S2],
]:
    """Create function that maps [`AwaitableFailure`][trcks.AwaitableFailure] values
    to [`AwaitableResultTuple`][trcks.AwaitableResultTuple] values.

    [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple] values are left unchanged.

    Args:
        callable_: Asynchronous function to apply to
            [`AwaitableFailure`][trcks.AwaitableFailure] values.
        *args:
            Positional arguments to be passed to `callable_`.
        **kwargs:
            Keyword arguments to be passed to `callable_`.

    Returns:
        Maps [`AwaitableFailure`][trcks.AwaitableFailure] values to new
            [`AwaitableResultTuple`][trcks.AwaitableResultTuple] values according to the
            given asynchronous function and leaves
            [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple] values unchanged.

    Examples:
        >>> import asyncio
        >>> from trcks import Result
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> async def _slowly_recover_from_not_found(e: str) -> Result[str, int]:
        ...     await asyncio.sleep(0.001)
        ...     if e == "not found":
        ...         return "success", 0
        ...     return "failure", e
        ...
        >>> slowly_recover_from_not_found = art.map_failure_to_awaitable_result(
        ...     _slowly_recover_from_not_found
        ... )
        >>> a_r_tpl_1 = slowly_recover_from_not_found(
        ...     art.construct_failure("not found")
        ... )
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('success', (0,))
        >>> a_r_tpl_2 = slowly_recover_from_not_found(art.construct_failure("fatal"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('failure', 'fatal')
        >>> a_r_tpl_3 = slowly_recover_from_not_found(
        ...     art.construct_successes_from_iterable([1, 2])
        ... )
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_3))
        ('success', (1, 2))
    """
    return map_failure_to_awaitable_result_iterable(
        compose(callable_, construct_from_awaitable_result), *args, **kwargs
    )


def map_failure_to_awaitable_result_iterable(
    callable_: Callable[Concatenate[_F1, _P], AwaitableResultIterable[_F2, _S2]],
    /,
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[
    [AwaitableResultTuple[_F1, _S1]],
    AwaitableResultTuple[_F2, _S1 | _S2],
]:
    """Create function that maps [`AwaitableFailure`][trcks.AwaitableFailure] values
    to [`AwaitableResultTuple`][trcks.AwaitableResultTuple] values.

    [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple] values are left unchanged.

    Args:
        callable_: Asynchronous function to apply to
            [`AwaitableFailure`][trcks.AwaitableFailure] values.
        *args:
            Positional arguments to be passed to `callable_`.
        **kwargs:
            Keyword arguments to be passed to `callable_`.

    Returns:
        Maps [`AwaitableFailure`][trcks.AwaitableFailure] values to new
            [`AwaitableResultTuple`][trcks.AwaitableResultTuple] values according to the
            given asynchronous function and leaves
            [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple] values unchanged.

    Examples:
        >>> import asyncio
        >>> from trcks import ResultTuple
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> async def _slowly_recover_from_not_found(e: str) -> ResultTuple[str, int]:
        ...     await asyncio.sleep(0.001)
        ...     if e == "not found":
        ...         return "success", (0,)
        ...     return "failure", e
        ...
        >>> slowly_recover_from_not_found = (
        ...     art.map_failure_to_awaitable_result_iterable(
        ...         _slowly_recover_from_not_found
        ...     )
        ... )
        >>> a_r_tpl_1 = slowly_recover_from_not_found(
        ...     art.construct_failure("not found")
        ... )
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('success', (0,))
        >>> a_r_tpl_2 = slowly_recover_from_not_found(art.construct_failure("fatal"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('failure', 'fatal')
        >>> a_r_tpl_3 = slowly_recover_from_not_found(
        ...     art.construct_successes_from_iterable((1, 2))
        ... )
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_3))
        ('success', (1, 2))
    """

    async def partially_mapped_callable(
        r_tpl: ResultTuple[_F1, _S1],
    ) -> ResultTuple[_F2, _S1 | _S2]:
        match r_tpl:
            case ("failure", value):
                return rt.construct_from_result_iterable(
                    await callable_(value, *args, **kwargs)
                )
            case ("success", _):
                return r_tpl
            case _:  # pragma: no cover
                assert_type(r_tpl, Never)  # type: ignore[unreachable]  # pyright: ignore[reportUnreachable]
                msg = f"{type(r_tpl).__name__!r} is not a valid ResultTuple"
                raise TypeError(msg)

    return a.map_to_awaitable(partially_mapped_callable)


def map_failure_to_iterable(
    callable_: Callable[Concatenate[_F1, _P], Iterable[_S2]],
    /,
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[
    [AwaitableResultTuple[_F1, _S1]],
    Awaitable[SuccessTuple[_S1] | SuccessTuple[_S2]],
]:
    """Create function that maps [`AwaitableFailure`][trcks.AwaitableFailure] values
    to [`Iterable`][collections.abc.Iterable]s.

    [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple] values are left unchanged.

    Args:
        callable_: Synchronous function to apply to
            [`AwaitableFailure`][trcks.AwaitableFailure] values.
        *args:
            Positional arguments to be passed to `callable_`.
        **kwargs:
            Keyword arguments to be passed to `callable_`.

    Returns:
        Maps [`AwaitableFailure`][trcks.AwaitableFailure] values to
            [`Iterable`][collections.abc.Iterable]s
            wrapped in [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple] values and
            leaves [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple] values
            unchanged.

    Examples:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> def _recover_from_not_found(description: str) -> tuple[int, ...]:
        ...     if description == "not found":
        ...         return (0,)
        ...     return ()
        ...
        >>> recover_from_not_found = art.map_failure_to_iterable(
        ...     _recover_from_not_found
        ... )
        >>> a_r_tpl_1 = recover_from_not_found(art.construct_failure("not found"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('success', (0,))
        >>> a_r_tpl_2 = recover_from_not_found(art.construct_failure("fatal"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('success', ())
        >>> a_r_tpl_3 = recover_from_not_found(
        ...     art.construct_successes_from_iterable((1, 2))
        ... )
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_3))
        ('success', (1, 2))
    """
    return a.map_(rt.map_failure_to_iterable(callable_, *args, **kwargs))


def map_failure_to_result(
    callable_: Callable[Concatenate[_F1, _P], Result[_F2, _S2]],
    /,
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[
    [AwaitableResultTuple[_F1, _S1]],
    AwaitableResultTuple[_F2, _S1 | _S2],
]:
    """Create function that maps [`AwaitableFailure`][trcks.AwaitableFailure] values
    to [`AwaitableResultTuple`][trcks.AwaitableResultTuple] values.

    [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple] values are left unchanged.

    Args:
        callable_: Synchronous function to apply to
            [`AwaitableFailure`][trcks.AwaitableFailure] values.
        *args:
            Positional arguments to be passed to `callable_`.
        **kwargs:
            Keyword arguments to be passed to `callable_`.

    Returns:
        Maps [`AwaitableFailure`][trcks.AwaitableFailure] values to new
            [`AwaitableResultTuple`][trcks.AwaitableResultTuple] values according to the
            given function and leaves
            [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple] values unchanged.

    Examples:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> def _recover_from_not_found(description: str) -> Result[str, int]:
        ...     if description == "not found":
        ...         return "success", 0
        ...     return "failure", description
        ...
        >>> recover_from_not_found = art.map_failure_to_result(_recover_from_not_found)
        >>> a_r_tpl_1 = recover_from_not_found(art.construct_failure("not found"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('success', (0,))
        >>> a_r_tpl_2 = recover_from_not_found(art.construct_failure("fatal"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('failure', 'fatal')
        >>> a_r_tpl_3 = recover_from_not_found(
        ...     art.construct_successes_from_iterable((1, 2))
        ... )
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_3))
        ('success', (1, 2))
    """
    return a.map_(rt.map_failure_to_result(callable_, *args, **kwargs))


def map_failure_to_result_iterable(
    callable_: Callable[Concatenate[_F1, _P], ResultIterable[_F2, _S2]],
    /,
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[
    [AwaitableResultTuple[_F1, _S1]],
    AwaitableResultTuple[_F2, _S1 | _S2],
]:
    """Create function that maps [`AwaitableFailure`][trcks.AwaitableFailure] values
    to [`AwaitableResultTuple`][trcks.AwaitableResultTuple] values.

    [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple] values are left unchanged.

    Args:
        callable_: Synchronous function to apply to
            [`AwaitableFailure`][trcks.AwaitableFailure] values.
        *args:
            Positional arguments to be passed to `callable_`.
        **kwargs:
            Keyword arguments to be passed to `callable_`.

    Returns:
        Maps [`AwaitableFailure`][trcks.AwaitableFailure] values to new
            [`AwaitableResultTuple`][trcks.AwaitableResultTuple] values according to the
            given function and leaves
            [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple] values unchanged.

    Examples:
        >>> import asyncio
        >>> from trcks import ResultTuple
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> def _recover_from_not_found(description: str) -> ResultTuple[str, int]:
        ...     if description == "not found":
        ...         return "success", (0,)
        ...     return "failure", description
        ...
        >>> recover_from_not_found = art.map_failure_to_result_iterable(
        ...     _recover_from_not_found
        ... )
        >>> a_r_tpl_1 = recover_from_not_found(art.construct_failure("not found"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('success', (0,))
        >>> a_r_tpl_2 = recover_from_not_found(art.construct_failure("fatal"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('failure', 'fatal')
        >>> a_r_tpl_3 = recover_from_not_found(
        ...     art.construct_successes_from_iterable((1, 2))
        ... )
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_3))
        ('success', (1, 2))
    """
    return a.map_(rt.map_failure_to_result_iterable(callable_, *args, **kwargs))


def map_successes(
    callable_: Callable[Concatenate[_S1, _P], _S2],
    /,
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[AwaitableResultTuple[_F1, _S1]], AwaitableResultTuple[_F1, _S2]]:
    """Map a synchronous function over each element
    in an [`AwaitableResultTuple`][trcks.AwaitableResultTuple].

    [`AwaitableFailure`][trcks.AwaitableFailure] values are left unchanged.

    Args:
        callable_: Function to apply to each success element.
        *args:
            Positional arguments to be passed to `callable_`.
        **kwargs:
            Keyword arguments to be passed to `callable_`.

    Returns:
        Function that transforms [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple]
            values
            element-wise.

    Examples:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> def _double_integer(n: int) -> int:
        ...     return n * 2
        ...
        >>> double_integers = art.map_successes(_double_integer)
        >>> a_r_tpl_1 = double_integers(
        ...     art.construct_successes_from_iterable((1, 2, 3))
        ... )
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('success', (2, 4, 6))
        >>> a_r_tpl_2 = double_integers(art.construct_failure("not found"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('failure', 'not found')
    """
    return a.map_(rt.map_successes(callable_, *args, **kwargs))


def map_successes_to_awaitable(
    callable_: Callable[Concatenate[_S1, _P], Awaitable[_S2]],
    /,
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[AwaitableResultTuple[_F1, _S1]], AwaitableResultTuple[_F1, _S2]]:
    """Map an awaitable-returning function over each element
    in an [`AwaitableResultTuple`][trcks.AwaitableResultTuple].

    [`AwaitableFailure`][trcks.AwaitableFailure] values are left unchanged.

    Args:
        callable_: Asynchronous function to apply to each success element.
        *args:
            Positional arguments to be passed to `callable_`.
        **kwargs:
            Keyword arguments to be passed to `callable_`.

    Returns:
        Function that transforms [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple]
            values
            element-wise using the given asynchronous function.

    Examples:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> async def _slowly_double_integer(n: int) -> int:
        ...     await asyncio.sleep(0.001)
        ...     return n * 2
        ...
        >>> slowly_double_integers = art.map_successes_to_awaitable(
        ...     _slowly_double_integer
        ... )
        >>> a_r_tpl_1 = slowly_double_integers(
        ...     art.construct_successes_from_iterable((1, 2, 3))
        ... )
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('success', (2, 4, 6))
        >>> a_r_tpl_2 = slowly_double_integers(art.construct_failure("not found"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('failure', 'not found')
    """
    return map_successes_to_awaitable_result_iterable(
        compose(callable_, construct_successes_from_awaitable), *args, **kwargs
    )


def map_successes_to_awaitable_iterable(
    callable_: Callable[Concatenate[_S1, _P], AwaitableIterable[_S2]],
    /,
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[AwaitableResultTuple[_F1, _S1]], AwaitableResultTuple[_F1, _S2]]:
    """Map an awaitable-[`Iterable`][collections.abc.Iterable]-returning function
    over each element in an [`AwaitableResultTuple`][trcks.AwaitableResultTuple].

    [`AwaitableFailure`][trcks.AwaitableFailure] values are left unchanged.

    Args:
        callable_: Asynchronous function to apply to each success element.
        *args:
            Positional arguments to be passed to `callable_`.
        **kwargs:
            Keyword arguments to be passed to `callable_`.

    Returns:
        Function that flat-maps [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple]
            values
            element-wise using the given asynchronous function.

    Examples:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> async def _slowly_duplicate_integer(n: int) -> tuple[int, int]:
        ...     await asyncio.sleep(0.001)
        ...     return n, n
        ...
        >>> slowly_duplicate_integers = art.map_successes_to_awaitable_iterable(
        ...     _slowly_duplicate_integer
        ... )
        >>> a_r_tpl_1 = slowly_duplicate_integers(
        ...     art.construct_successes_from_iterable([1, 2])
        ... )
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('success', (1, 1, 2, 2))
        >>> a_r_tpl_2 = slowly_duplicate_integers(art.construct_failure("oops"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('failure', 'oops')
    """
    return map_successes_to_awaitable_result_iterable(
        compose(callable_, construct_successes_from_awaitable_iterable), *args, **kwargs
    )


def map_successes_to_awaitable_result(
    callable_: Callable[Concatenate[_S1, _P], AwaitableResult[_F2, _S2]],
    /,
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[
    [AwaitableResultTuple[_F1, _S1]],
    AwaitableResultTuple[_F1 | _F2, _S2],
]:
    """Map an [`AwaitableResult`][trcks.AwaitableResult]-returning function over each
    element in an [`AwaitableResultTuple`][trcks.AwaitableResultTuple].

    [`AwaitableFailure`][trcks.AwaitableFailure] values are left unchanged.
    Short-circuits on the first failure returned by `callable_`.

    Args:
        callable_: Asynchronous function to apply to each success element.
        *args:
            Positional arguments to be passed to `callable_`.
        **kwargs:
            Keyword arguments to be passed to `callable_`.

    Returns:
        Function that maps over [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple]
            values and
            returns the first [`AwaitableFailure`][trcks.AwaitableFailure] encountered,
            if any.

    Examples:
        >>> import asyncio
        >>> from trcks import Result
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> async def _slowly_double_integer_if_positive(n: int) -> Result[str, int]:
        ...     await asyncio.sleep(0.001)
        ...     if n <= 0:
        ...         return "failure", "negative"
        ...     return "success", n * 2
        ...
        >>> slowly_double_integers_if_positive = art.map_successes_to_awaitable_result(
        ...     _slowly_double_integer_if_positive
        ... )
        >>> a_r_tpl_1 = slowly_double_integers_if_positive(
        ...     art.construct_successes_from_iterable((1, 2))
        ... )
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('success', (2, 4))
        >>> a_r_tpl_2 = slowly_double_integers_if_positive(
        ...     art.construct_successes_from_iterable((1, -1, 2))
        ... )
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('failure', 'negative')
        >>> a_r_tpl_3 = slowly_double_integers_if_positive(
        ...     art.construct_failure("oops")
        ... )
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_3))
        ('failure', 'oops')
    """
    return map_successes_to_awaitable_result_iterable(
        compose(callable_, construct_from_awaitable_result), *args, **kwargs
    )


def map_successes_to_awaitable_result_iterable(
    callable_: Callable[Concatenate[_S1, _P], AwaitableResultIterable[_F2, _S2]],
    /,
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[
    [AwaitableResultTuple[_F1, _S1]],
    AwaitableResultTuple[_F1 | _F2, _S2],
]:
    """Map an [`AwaitableResultIterable`][trcks.AwaitableResultIterable]-returning
    function over each element in an
    [`AwaitableResultTuple`][trcks.AwaitableResultTuple].

    [`AwaitableFailure`][trcks.AwaitableFailure] values are left unchanged.
    Short-circuits on the first failure returned by `callable_`.

    Args:
        callable_: Asynchronous function to apply to each success element.
        *args:
            Positional arguments to be passed to `callable_`.
        **kwargs:
            Keyword arguments to be passed to `callable_`.

    Returns:
        Function that flat-maps [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple]
            values and
            short-circuits on the first [`AwaitableFailure`][trcks.AwaitableFailure]
            returned by `callable_`.

    Examples:
        >>> import asyncio
        >>> from trcks import ResultTuple
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> async def _slowly_duplicate_integer_if_positive(
        ...     n: int,
        ... ) -> ResultTuple[str, int]:
        ...     await asyncio.sleep(0.001)
        ...     if n <= 0:
        ...         return "failure", "negative"
        ...     return "success", (n, n)
        ...
        >>> slowly_duplicate_integers_if_positive = (
        ...     art.map_successes_to_awaitable_result_iterable(
        ...         _slowly_duplicate_integer_if_positive
        ...     )
        ... )
        >>> a_r_tpl_1 = slowly_duplicate_integers_if_positive(
        ...     art.construct_successes_from_iterable((1, 2))
        ... )
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('success', (1, 1, 2, 2))
        >>> a_r_tpl_2 = slowly_duplicate_integers_if_positive(
        ...     art.construct_successes_from_iterable((1, -1, 2))
        ... )
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('failure', 'negative')
        >>> a_r_tpl_3 = slowly_duplicate_integers_if_positive(
        ...     art.construct_failure("oops")
        ... )
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_3))
        ('failure', 'oops')
    """

    async def partially_mapped_callable(
        r_tpl: ResultTuple[_F1, _S1],
    ) -> ResultTuple[_F1 | _F2, _S2]:
        match r_tpl:
            case ("failure", _):
                return r_tpl
            case ("success", s1s):
                s2s: list[_S2] = []
                for s1 in s1s:
                    match await callable_(s1, *args, **kwargs):
                        case ("failure", _) as output_r_tpl:
                            return output_r_tpl
                        case ("success", additional_s2s):
                            s2s.extend(additional_s2s)
                        case _ as output_r_tpl:  # pragma: no cover
                            assert_type(output_r_tpl, Never)  # type: ignore[unreachable]  # pyright: ignore[reportUnreachable]
                            msg = (
                                f"{type(output_r_tpl).__name__!r} is not a valid "
                                "ResultIterable"
                            )
                            raise TypeError(msg)
                return "success", tuple(s2s)
            case _:  # pragma: no cover
                assert_type(r_tpl, Never)  # type: ignore[unreachable]  # pyright: ignore[reportUnreachable]
                msg = f"{type(r_tpl).__name__!r} is not a valid ResultTuple"
                raise TypeError(msg)

    return a.map_to_awaitable(partially_mapped_callable)


def map_successes_to_iterable(
    callable_: Callable[Concatenate[_S1, _P], Iterable[_S2]],
    /,
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[AwaitableResultTuple[_F1, _S1]], AwaitableResultTuple[_F1, _S2]]:
    """Map an [`Iterable`][collections.abc.Iterable]-returning function over each
    element in an [`AwaitableResultTuple`][trcks.AwaitableResultTuple].

    [`AwaitableFailure`][trcks.AwaitableFailure] values are left unchanged.

    Args:
        callable_: Synchronous function to apply to each success element.
        *args:
            Positional arguments to be passed to `callable_`.
        **kwargs:
            Keyword arguments to be passed to `callable_`.

    Returns:
        Function that flat-maps over
        [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple] values.

    Examples:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> def _duplicate_integer(n: int) -> tuple[int, int]:
        ...     return n, n
        ...
        >>> duplicate_integers = art.map_successes_to_iterable(_duplicate_integer)
        >>> a_r_tpl = duplicate_integers(art.construct_successes_from_iterable((1, 2)))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl))
        ('success', (1, 1, 2, 2))
    """
    return a.map_(rt.map_successes_to_iterable(callable_, *args, **kwargs))


def map_successes_to_result(
    callable_: Callable[Concatenate[_S1, _P], Result[_F2, _S2]],
    /,
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[
    [AwaitableResultTuple[_F1, _S1]],
    AwaitableResultTuple[_F1 | _F2, _S2],
]:
    """Map a result-returning function over each element
    in an [`AwaitableResultTuple`][trcks.AwaitableResultTuple].

    [`AwaitableFailure`][trcks.AwaitableFailure] values are left unchanged.
    Short-circuits on the first failure returned by `callable_`.

    Args:
        callable_: Synchronous function to apply to each success element.
        *args:
            Positional arguments to be passed to `callable_`.
        **kwargs:
            Keyword arguments to be passed to `callable_`.

    Returns:
        Function that maps over [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple]
            values and
            returns the first [`AwaitableFailure`][trcks.AwaitableFailure] encountered,
            if any.

    Examples:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> def _double_integer_if_positive(n: int) -> Result[str, int]:
        ...     if n <= 0:
        ...         return "failure", "negative"
        ...     return "success", n * 2
        ...
        >>> double_integers_if_positive = art.map_successes_to_result(
        ...     _double_integer_if_positive
        ... )
        >>> a_r_tpl_1 = double_integers_if_positive(
        ...     art.construct_successes_from_iterable((1, 2))
        ... )
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('success', (2, 4))
        >>> a_r_tpl_2 = double_integers_if_positive(
        ...     art.construct_successes_from_iterable((1, -1, 2))
        ... )
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('failure', 'negative')
        >>> a_r_tpl_3 = double_integers_if_positive(art.construct_failure("oops"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_3))
        ('failure', 'oops')
    """
    return a.map_(rt.map_successes_to_result(callable_, *args, **kwargs))


def map_successes_to_result_iterable(
    callable_: Callable[Concatenate[_S1, _P], ResultIterable[_F2, _S2]],
    /,
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[
    [AwaitableResultTuple[_F1, _S1]],
    AwaitableResultTuple[_F1 | _F2, _S2],
]:
    """Map a [`ResultIterable`][trcks.ResultIterable]-returning function over each
    element in an [`AwaitableResultTuple`][trcks.AwaitableResultTuple].

    [`AwaitableFailure`][trcks.AwaitableFailure] values are left unchanged.
    Short-circuits on the first failure returned by `callable_`.

    Args:
        callable_: Synchronous function to apply to each success element.
        *args:
            Positional arguments to be passed to `callable_`.
        **kwargs:
            Keyword arguments to be passed to `callable_`.

    Returns:
        Function that flat-maps [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple]
            values and
            short-circuits on the first [`AwaitableFailure`][trcks.AwaitableFailure]
            returned by `callable_`.

    Examples:
        >>> import asyncio
        >>> from trcks import ResultTuple
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> def _duplicate_integer_if_positive(n: int) -> ResultTuple[str, int]:
        ...     if n <= 0:
        ...         return "failure", "negative"
        ...     return "success", (n, n)
        ...
        >>> duplicate_integers_if_positive = art.map_successes_to_result_iterable(
        ...     _duplicate_integer_if_positive
        ... )
        >>> a_r_tpl_1 = duplicate_integers_if_positive(
        ...     art.construct_successes_from_iterable((1, 2))
        ... )
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('success', (1, 1, 2, 2))
        >>> a_r_tpl_2 = duplicate_integers_if_positive(art.construct_failure("oops"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('failure', 'oops')
    """
    return a.map_(rt.map_successes_to_result_iterable(callable_, *args, **kwargs))


def tap_failure(
    callable_: Callable[Concatenate[_F1, _P], object],
    /,
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[AwaitableResultTuple[_F1, _S1]], AwaitableResultTuple[_F1, _S1]]:
    """Apply a synchronous side effect to [`AwaitableFailure`][trcks.AwaitableFailure]
    values.

    [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple] values are passed on without
    side effects.

    Args:
        callable_: Synchronous side effect to apply
            to the [`AwaitableFailure`][trcks.AwaitableFailure] value.
        *args:
            Positional arguments to be passed to `callable_`.
        **kwargs:
            Keyword arguments to be passed to `callable_`.

    Returns:
        Applies the given side effect to [`AwaitableFailure`][trcks.AwaitableFailure]
            values and
            returns the original [`AwaitableFailure`][trcks.AwaitableFailure] value.
            Passes on [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple] values
            without side effects.

    Examples:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> def _log_failure(description: str) -> None:
        ...     print(f"Failure: {description}")
        ...
        >>> log_failure = art.tap_failure(_log_failure)
        >>> a_r_tpl_1 = log_failure(art.construct_failure("oops"))
        >>> r_tpl_1 = asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        Failure: oops
        >>> r_tpl_1
        ('failure', 'oops')
        >>> a_r_tpl_2 = log_failure(art.construct_successes_from_iterable((1,)))
        >>> r_tpl_2 = asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        >>> r_tpl_2
        ('success', (1,))
    """
    return a.map_(rt.tap_failure(callable_, *args, **kwargs))


def tap_failure_to_awaitable(
    callable_: Callable[Concatenate[_F1, _P], Awaitable[object]],
    /,
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[AwaitableResultTuple[_F1, _S1]], AwaitableResultTuple[_F1, _S1]]:
    """Apply an asynchronous side effect to [`AwaitableFailure`][trcks.AwaitableFailure]
    values.

    [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple] values are passed on without
    side effects.

    Args:
        callable_: Asynchronous side effect to apply
            to the [`AwaitableFailure`][trcks.AwaitableFailure] value.
        *args:
            Positional arguments to be passed to `callable_`.
        **kwargs:
            Keyword arguments to be passed to `callable_`.

    Returns:
        Applies the given side effect to [`AwaitableFailure`][trcks.AwaitableFailure]
            values and
            returns the original [`AwaitableFailure`][trcks.AwaitableFailure] value.
            Passes on [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple] values
            without side effects.

    Examples:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> async def _slowly_log_failure(e: str) -> None:
        ...     await asyncio.sleep(0.001)
        ...     print(f"Failure: {e}")
        ...
        >>> slowly_log_failure = art.tap_failure_to_awaitable(_slowly_log_failure)
        >>> a_r_tpl_1 = slowly_log_failure(art.construct_failure("oops"))
        >>> r_tpl_1 = asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        Failure: oops
        >>> r_tpl_1
        ('failure', 'oops')
        >>> a_r_tpl_2 = slowly_log_failure(art.construct_successes_from_iterable((1,)))
        >>> r_tpl_2 = asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        >>> r_tpl_2
        ('success', (1,))
    """

    async def bypassed_callable(value: _F1) -> _F1:
        _ = await callable_(value, *args, **kwargs)
        return value

    return map_failure_to_awaitable(bypassed_callable)


def tap_failure_to_awaitable_iterable(
    callable_: Callable[Concatenate[_F1, _P], AwaitableIterable[object]],
    /,
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[
    [AwaitableResultTuple[_F1, _S1]],
    Awaitable[SuccessTuple[_F1] | SuccessTuple[_S1]],
]:
    """Apply an asynchronous [`Iterable`][collections.abc.Iterable]-returning side
    effect to [`AwaitableFailure`][trcks.AwaitableFailure] values.

    The number of side effect outputs determines how many times the original
    failure value is repeated. The failure is converted to an
    [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple].

    [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple] values are passed on without
    side effects.

    Args:
        callable_: Asynchronous side effect to apply
            to the [`AwaitableFailure`][trcks.AwaitableFailure] value.
        *args:
            Positional arguments to be passed to `callable_`.
        **kwargs:
            Keyword arguments to be passed to `callable_`.

    Returns:
        Applies the given side effect to [`AwaitableFailure`][trcks.AwaitableFailure]
            values and
            converts them to [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple]
            values containing the original failure repeated once per element in the
            [`Iterable`][collections.abc.Iterable] returned by the side effect. Passes
            on [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple] values without
            side effects.

    Examples:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> async def _slowly_log_and_alert(description: str) -> tuple[None, None]:
        ...     await asyncio.sleep(0.001)
        ...     return (
        ...         print(f"Failure: {description}"),
        ...         print(f"Logged: {description}"),
        ...     )
        ...
        >>> slowly_log_and_alert = art.tap_failure_to_awaitable_iterable(
        ...     _slowly_log_and_alert
        ... )
        >>> a_r_tpl_1 = slowly_log_and_alert(art.construct_failure("critical"))
        >>> r_tpl_1 = asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        Failure: critical
        Logged: critical
        >>> r_tpl_1
        ('success', ('critical', 'critical'))
        >>> a_r_tpl_2 = slowly_log_and_alert(
        ...     art.construct_successes_from_iterable([1])
        ... )
        >>> r_tpl_2 = asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        >>> r_tpl_2
        ('success', (1,))
    """

    async def bypassed_callable(value: _F1) -> list[_F1]:
        return [value for _ in await callable_(value, *args, **kwargs)]

    return map_failure_to_awaitable_iterable(bypassed_callable)


def tap_failure_to_awaitable_result(
    callable_: Callable[Concatenate[_F1, _P], AwaitableResult[object, _S2]],
    /,
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[
    [AwaitableResultTuple[_F1, _S1]],
    AwaitableResultTuple[_F1, _S1 | _S2],
]:
    """Apply an asynchronous side effect with return type [`Result`][trcks.Result]
    to [`AwaitableFailure`][trcks.AwaitableFailure] values.

    [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple] values are passed on without
    side effects.

    Args:
        callable_: Asynchronous side effect to apply
            to the [`AwaitableFailure`][trcks.AwaitableFailure] value.
        *args:
            Positional arguments to be passed to `callable_`.
        **kwargs:
            Keyword arguments to be passed to `callable_`.

    Returns:
        Applies the given side effect to [`AwaitableFailure`][trcks.AwaitableFailure]
            values.
            If the given side effect returns an
            [`AwaitableFailure`][trcks.AwaitableFailure], *the original*
            [`AwaitableFailure`][trcks.AwaitableFailure] value is returned. If the given
            side effect returns an [`AwaitableSuccess`][trcks.AwaitableSuccess], *this*
            [`AwaitableSuccess`][trcks.AwaitableSuccess] is returned (wrapped as a
            tuple). Passes on [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple]
            values without side effects.

    Examples:
        >>> import asyncio
        >>> from trcks import Result
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> async def _slowly_recover_from_not_found(e: str) -> Result[str, int]:
        ...     await asyncio.sleep(0.001)
        ...     if e == "not found":
        ...         return "success", 0
        ...     return "failure", e
        ...
        >>> slowly_recover_from_not_found = art.tap_failure_to_awaitable_result(
        ...     _slowly_recover_from_not_found
        ... )
        >>> a_r_tpl_1 = slowly_recover_from_not_found(
        ...     art.construct_failure("not found")
        ... )
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('success', (0,))
        >>> a_r_tpl_2 = slowly_recover_from_not_found(art.construct_failure("fatal"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('failure', 'fatal')
    """

    async def bypassed_callable(value: _F1) -> ResultTuple[_F1, _S2]:
        match await callable_(value, *args, **kwargs):
            case ("failure", _):
                return r.construct_failure(value)
            case ("success", s2):
                return rt.construct_successes(s2)
            case _ as rslt:  # pragma: no cover
                assert_type(rslt, Never)  # type: ignore[unreachable]  # pyright: ignore[reportUnreachable]
                msg = f"{type(rslt).__name__!r} is not a valid ResultTuple"
                raise TypeError(msg)

    return map_failure_to_awaitable_result_iterable(bypassed_callable)


def tap_failure_to_awaitable_result_iterable(
    callable_: Callable[Concatenate[_F1, _P], AwaitableResultIterable[object, _S2]],
    /,
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[
    [AwaitableResultTuple[_F1, _S1]],
    AwaitableResultTuple[_F1, _S1 | _S2],
]:
    """Apply an asynchronous side effect with return type
    [`ResultIterable`][trcks.ResultIterable] to
    [`AwaitableFailure`][trcks.AwaitableFailure] values.

    [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple] values are passed on without
    side effects.

    Args:
        callable_: Asynchronous side effect to apply
            to the [`AwaitableFailure`][trcks.AwaitableFailure] value.
        *args:
            Positional arguments to be passed to `callable_`.
        **kwargs:
            Keyword arguments to be passed to `callable_`.

    Returns:
        Applies the given side effect to [`AwaitableFailure`][trcks.AwaitableFailure]
            values.
            If the given side effect returns an
            [`AwaitableFailure`][trcks.AwaitableFailure], *the original*
            [`AwaitableFailure`][trcks.AwaitableFailure] value is returned. If the given
            side effect returns an
            [`AwaitableSuccessIterable`][trcks.AwaitableSuccessIterable], *this*
            [`AwaitableSuccessIterable`][trcks.AwaitableSuccessIterable] is returned as
            an [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple]. Passes on
            [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple] values without side
            effects.

    Examples:
        >>> import asyncio
        >>> from trcks import ResultTuple
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> async def _slowly_recover_from_not_found(e: str) -> ResultTuple[str, int]:
        ...     await asyncio.sleep(0.001)
        ...     if e == "not found":
        ...         return "success", (0,)
        ...     return "failure", e
        ...
        >>> slowly_recover_from_not_found = (
        ...     art.tap_failure_to_awaitable_result_iterable(
        ...         _slowly_recover_from_not_found,
        ...     )
        ... )
        >>> a_r_tpl_1 = slowly_recover_from_not_found(
        ...     art.construct_failure("not found")
        ... )
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('success', (0,))
        >>> a_r_tpl_2 = slowly_recover_from_not_found(art.construct_failure("fatal"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('failure', 'fatal')
    """

    async def bypassed_callable(value: _F1) -> ResultIterable[_F1, _S2]:
        match await callable_(value, *args, **kwargs):
            case ("failure", _):
                return r.construct_failure(value)
            case ("success", _) as r_it:
                return r_it
            case _ as r_it:  # pragma: no cover
                assert_type(r_it, Never)  # type: ignore[unreachable]  # pyright: ignore[reportUnreachable]
                msg = f"{type(r_it).__name__!r} is not a valid ResultIterable"
                raise TypeError(msg)

    return map_failure_to_awaitable_result_iterable(bypassed_callable)


def tap_failure_to_iterable(
    callable_: Callable[Concatenate[_F1, _P], Iterable[object]],
    /,
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[
    [AwaitableResultTuple[_F1, _S1]],
    Awaitable[SuccessTuple[_F1] | SuccessTuple[_S1]],
]:
    """Apply an [`Iterable`][collections.abc.Iterable]-returning side effect
    to [`AwaitableFailure`][trcks.AwaitableFailure] values.

    The number of side effect outputs determines how many times the original
    failure value is repeated. The failure is converted to an
    [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple].

    [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple] values are passed on without
    side effects.

    Args:
        callable_: Synchronous side effect to apply
            to the [`AwaitableFailure`][trcks.AwaitableFailure] value.
        *args:
            Positional arguments to be passed to `callable_`.
        **kwargs:
            Keyword arguments to be passed to `callable_`.

    Returns:
        Applies the given side effect to [`AwaitableFailure`][trcks.AwaitableFailure]
            values and
            converts them to [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple]
            values containing the original failure repeated once per element in the
            [`Iterable`][collections.abc.Iterable] returned by the side effect. Passes
            on [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple] values without
            side effects.

    Examples:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> def _log_and_alert(description: str) -> tuple[None, None]:
        ...     return (
        ...         print(f"Failure: {description}"),
        ...         print(f"Logged: {description}"),
        ...     )
        ...
        >>> log_and_alert = art.tap_failure_to_iterable(_log_and_alert)
        >>> a_r_tpl_1 = log_and_alert(art.construct_failure("critical"))
        >>> r_tpl_1 = asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        Failure: critical
        Logged: critical
        >>> r_tpl_1
        ('success', ('critical', 'critical'))
        >>> a_r_tpl_2 = log_and_alert(art.construct_successes_from_iterable((1,)))
        >>> r_tpl_2 = asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        >>> r_tpl_2
        ('success', (1,))
    """
    return a.map_(rt.tap_failure_to_iterable(callable_, *args, **kwargs))


def tap_failure_to_result(
    callable_: Callable[Concatenate[_F1, _P], Result[object, _S2]],
    /,
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[
    [AwaitableResultTuple[_F1, _S1]],
    AwaitableResultTuple[_F1, _S1 | _S2],
]:
    """Apply a synchronous side effect with return type [`Result`][trcks.Result]
    to [`AwaitableFailure`][trcks.AwaitableFailure] values.

    [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple] values are passed on without
    side effects.

    Args:
        callable_: Synchronous side effect to apply
            to the [`AwaitableFailure`][trcks.AwaitableFailure] value.
        *args:
            Positional arguments to be passed to `callable_`.
        **kwargs:
            Keyword arguments to be passed to `callable_`.

    Returns:
        Applies the given side effect to [`AwaitableFailure`][trcks.AwaitableFailure]
            values.
            If the given side effect returns a [`Failure`][trcks.Failure], *the
            original* [`AwaitableFailure`][trcks.AwaitableFailure] value is returned. If
            the given side effect returns a [`Success`][trcks.Success], *this*
            [`Success`][trcks.Success] is returned (wrapped as a tuple). Passes on
            [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple] values without side
            effects.

    Examples:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> def _recover_from_not_found(description: str) -> Result[None, int]:
        ...     if description == "not found":
        ...         return "success", 0
        ...     return "failure", None
        ...
        >>> recover_from_not_found = art.tap_failure_to_result(_recover_from_not_found)
        >>> a_r_tpl_1 = recover_from_not_found(art.construct_failure("not found"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('success', (0,))
        >>> a_r_tpl_2 = recover_from_not_found(art.construct_failure("fatal"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('failure', 'fatal')
        >>> a_r_tpl_3 = recover_from_not_found(
        ...     art.construct_successes_from_iterable((1,))
        ... )
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_3))
        ('success', (1,))
    """
    return a.map_(rt.tap_failure_to_result(callable_, *args, **kwargs))


def tap_failure_to_result_iterable(
    callable_: Callable[Concatenate[_F1, _P], ResultIterable[object, _S2]],
    /,
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[
    [AwaitableResultTuple[_F1, _S1]],
    AwaitableResultTuple[_F1, _S1 | _S2],
]:
    """Apply a synchronous side effect with return type
    [`ResultIterable`][trcks.ResultIterable] to
    [`AwaitableFailure`][trcks.AwaitableFailure] values.

    [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple] values are passed on without
    side effects.

    Args:
        callable_: Synchronous side effect to apply
            to the [`AwaitableFailure`][trcks.AwaitableFailure] value.
        *args:
            Positional arguments to be passed to `callable_`.
        **kwargs:
            Keyword arguments to be passed to `callable_`.

    Returns:
        Applies the given side effect to [`AwaitableFailure`][trcks.AwaitableFailure]
            values.
            If the given side effect returns a [`Failure`][trcks.Failure], *the
            original* [`AwaitableFailure`][trcks.AwaitableFailure] value is returned. If
            the given side effect returns a [`SuccessIterable`][trcks.SuccessIterable],
            *this* [`SuccessIterable`][trcks.SuccessIterable] is returned as a
            [`SuccessTuple`][trcks.SuccessTuple]. Passes on
            [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple] values without side
            effects.

    Examples:
        >>> import asyncio
        >>> from trcks import ResultTuple
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> def _recover_from_not_found(description: str) -> ResultTuple[None, int]:
        ...     if description == "not found":
        ...         return "success", (0,)
        ...     return "failure", None
        ...
        >>> recover_from_not_found = art.tap_failure_to_result_iterable(
        ...     _recover_from_not_found
        ... )
        >>> a_r_tpl_1 = recover_from_not_found(art.construct_failure("not found"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('success', (0,))
        >>> a_r_tpl_2 = recover_from_not_found(art.construct_failure("fatal"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('failure', 'fatal')
        >>> a_r_tpl_3 = recover_from_not_found(
        ...     art.construct_successes_from_iterable((1,))
        ... )
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_3))
        ('success', (1,))
    """
    return a.map_(rt.tap_failure_to_result_iterable(callable_, *args, **kwargs))


def tap_successes(
    callable_: Callable[Concatenate[_S1, _P], object],
    /,
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[AwaitableResultTuple[_F1, _S1]], AwaitableResultTuple[_F1, _S1]]:
    """Apply a synchronous side effect to each element
    in an [`AwaitableResultTuple`][trcks.AwaitableResultTuple].

    [`AwaitableFailure`][trcks.AwaitableFailure] values are passed on without side
    effects.

    Args:
        callable_: Synchronous side effect to apply to each success element.
        *args:
            Positional arguments to be passed to `callable_`.
        **kwargs:
            Keyword arguments to be passed to `callable_`.

    Returns:
        Applies the given side effect and returns the original
            [`AwaitableResultTuple`][trcks.AwaitableResultTuple] value.

    Examples:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> def _log_value(n: int) -> None:
        ...     print(f"Value: {n}")
        ...
        >>> log_values = art.tap_successes(_log_value)
        >>> a_r_tpl_1 = log_values(art.construct_successes_from_iterable((1, 2)))
        >>> r_tpl_1 = asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        Value: 1
        Value: 2
        >>> r_tpl_1
        ('success', (1, 2))
        >>> a_r_tpl_2 = log_values(art.construct_failure("oops"))
        >>> r_tpl_2 = asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        >>> r_tpl_2
        ('failure', 'oops')
    """
    return a.map_(rt.tap_successes(callable_, *args, **kwargs))


def tap_successes_to_awaitable(
    callable_: Callable[Concatenate[_S1, _P], Awaitable[object]],
    /,
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[AwaitableResultTuple[_F1, _S1]], AwaitableResultTuple[_F1, _S1]]:
    """Apply an asynchronous side effect to each element
    in an [`AwaitableResultTuple`][trcks.AwaitableResultTuple].

    [`AwaitableFailure`][trcks.AwaitableFailure] values are passed on without side
    effects.

    Args:
        callable_: Asynchronous side effect to apply to each success element.
        *args:
            Positional arguments to be passed to `callable_`.
        **kwargs:
            Keyword arguments to be passed to `callable_`.

    Returns:
        Applies the given side effect and returns the original
            [`AwaitableResultTuple`][trcks.AwaitableResultTuple] value.

    Examples:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> async def _slowly_log_value(n: int) -> None:
        ...     await asyncio.sleep(0.001)
        ...     print(f"Value: {n}")
        ...
        >>> slowly_log_values = art.tap_successes_to_awaitable(_slowly_log_value)
        >>> a_r_tpl_1 = slowly_log_values(art.construct_successes_from_iterable((1, 2)))
        >>> r_tpl_1 = asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        Value: 1
        Value: 2
        >>> r_tpl_1
        ('success', (1, 2))
        >>> a_r_tpl_2 = slowly_log_values(art.construct_failure("oops"))
        >>> r_tpl_2 = asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        >>> r_tpl_2
        ('failure', 'oops')
    """

    async def bypassed_callable(value: _S1) -> _S1:
        _ = await callable_(value, *args, **kwargs)
        return value

    return map_successes_to_awaitable(bypassed_callable)


def tap_successes_to_awaitable_iterable(
    callable_: Callable[Concatenate[_S1, _P], AwaitableIterable[object]],
    /,
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[AwaitableResultTuple[_F1, _S1]], AwaitableResultTuple[_F1, _S1]]:
    """Apply an asynchronous [`Iterable`][collections.abc.Iterable]-returning side
    effect to each element in an [`AwaitableResultTuple`][trcks.AwaitableResultTuple].

    The number of side effect outputs determines how many times each original
    element is repeated in the resulting tuple.

    [`AwaitableFailure`][trcks.AwaitableFailure] values are passed on without side
    effects.

    Args:
        callable_: Asynchronous side effect to apply to each success element.
        *args:
            Positional arguments to be passed to `callable_`.
        **kwargs:
            Keyword arguments to be passed to `callable_`.

    Returns:
        Applies the given side effect and returns an
            [`AwaitableResultTuple`][trcks.AwaitableResultTuple] where each original
            success element is repeated once per element returned by the side effect.

    Examples:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> async def _slowly_log_twice(n: int) -> tuple[None, None]:
        ...     await asyncio.sleep(0.001)
        ...     return print(f"Received: {n}"), print(f"Received: {n}")
        ...
        >>> slowly_log_twice = art.tap_successes_to_awaitable_iterable(
        ...     _slowly_log_twice
        ... )
        >>> a_r_tpl = slowly_log_twice(art.construct_successes_from_iterable([7]))
        >>> r_tpl = asyncio.run(art.to_coroutine_result_tuple(a_r_tpl))
        Received: 7
        Received: 7
        >>> r_tpl
        ('success', (7, 7))
    """

    async def bypassed_callable(value: _S1) -> list[_S1]:
        return [value for _ in await callable_(value, *args, **kwargs)]

    return map_successes_to_awaitable_iterable(bypassed_callable)


def tap_successes_to_awaitable_result(
    callable_: Callable[Concatenate[_S1, _P], AwaitableResult[_F2, object]],
    /,
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[
    [AwaitableResultTuple[_F1, _S1]],
    AwaitableResultTuple[_F1 | _F2, _S1],
]:
    """Apply an asynchronous side effect with return type [`Result`][trcks.Result]
    to each element in an [`AwaitableResultTuple`][trcks.AwaitableResultTuple].

    [`AwaitableFailure`][trcks.AwaitableFailure] values are passed on without side
    effects.

    Args:
        callable_: Asynchronous side effect to apply to each success element.
        *args:
            Positional arguments to be passed to `callable_`.
        **kwargs:
            Keyword arguments to be passed to `callable_`.

    Returns:
        Applies the given side effect to each success element.
            If the given side effect returns an
            [`AwaitableFailure`][trcks.AwaitableFailure], *this*
            [`AwaitableFailure`][trcks.AwaitableFailure] is returned. If the given side
            effect returns an [`AwaitableSuccess`][trcks.AwaitableSuccess], *the
            original* success element is returned.

    Examples:
        >>> import asyncio
        >>> from trcks import Result
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> async def _validate_positive(n: int) -> Result[str, None]:
        ...     await asyncio.sleep(0.001)
        ...     if n <= 0:
        ...         return "failure", "negative"
        ...     return "success", None
        ...
        >>> validate_positive = art.tap_successes_to_awaitable_result(
        ...     _validate_positive
        ... )
        >>> a_r_tpl_1 = validate_positive(art.construct_successes_from_iterable((1, 2)))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('success', (1, 2))
        >>> a_r_tpl_2 = validate_positive(
        ...     art.construct_successes_from_iterable((1, -1))
        ... )
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('failure', 'negative')
        >>> a_r_tpl_3 = validate_positive(art.construct_failure("oops"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_3))
        ('failure', 'oops')
    """
    return tap_successes_to_awaitable_result_iterable(
        compose(callable_, construct_from_awaitable_result), *args, **kwargs
    )


def tap_successes_to_awaitable_result_iterable(
    callable_: Callable[Concatenate[_S1, _P], AwaitableResultIterable[_F2, object]],
    /,
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[
    [AwaitableResultTuple[_F1, _S1]],
    AwaitableResultTuple[_F1 | _F2, _S1],
]:
    """Apply an asynchronous side effect with return type
    [`ResultIterable`][trcks.ResultIterable] to each element
    in an [`AwaitableResultTuple`][trcks.AwaitableResultTuple].

    [`AwaitableFailure`][trcks.AwaitableFailure] values are passed on without side
    effects.

    Args:
        callable_: Asynchronous side effect to apply to each success element.
        *args:
            Positional arguments to be passed to `callable_`.
        **kwargs:
            Keyword arguments to be passed to `callable_`.

    Returns:
        Applies the given side effect to each success element.
            If the given side effect returns an
            [`AwaitableFailure`][trcks.AwaitableFailure], *this*
            [`AwaitableFailure`][trcks.AwaitableFailure] is returned. If the given side
            effect returns an
            [`AwaitableSuccessIterable`][trcks.AwaitableSuccessIterable], *the original*
            success element is repeated once per element in the success iterable.

    Examples:
        >>> import asyncio
        >>> from trcks import ResultTuple
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> async def _validate_positive(n: int) -> ResultTuple[str, None]:
        ...     await asyncio.sleep(0.001)
        ...     if n <= 0:
        ...         return "failure", "negative"
        ...     return "success", (None, None)
        ...
        >>> validate_positive = art.tap_successes_to_awaitable_result_iterable(
        ...     _validate_positive
        ... )
        >>> a_r_tpl_1 = validate_positive(art.construct_successes_from_iterable((7,)))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('success', (7, 7))
        >>> a_r_tpl_2 = validate_positive(
        ...     art.construct_successes_from_iterable((1, -1))
        ... )
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('failure', 'negative')
        >>> a_r_tpl_3 = validate_positive(art.construct_failure("oops"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_3))
        ('failure', 'oops')
    """

    async def tapped_callable(s1: _S1) -> ResultIterable[_F2, _S1]:
        match await callable_(s1, *args, **kwargs):
            case ("failure", _) as r_it:
                return r_it
            case ("success", objs):
                return "success", tuple(s1 for _ in objs)
            case _ as r_it:  # pragma: no cover
                assert_type(r_it, Never)  # type: ignore[unreachable]  # pyright: ignore[reportUnreachable]
                msg = f"{type(r_it).__name__!r} is not a valid ResultIterable"
                raise TypeError(msg)

    return map_successes_to_awaitable_result_iterable(tapped_callable)


def tap_successes_to_iterable(
    callable_: Callable[Concatenate[_S1, _P], Iterable[object]],
    /,
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[[AwaitableResultTuple[_F1, _S1]], AwaitableResultTuple[_F1, _S1]]:
    """Apply an [`Iterable`][collections.abc.Iterable]-returning side effect to each
    element in an [`AwaitableResultTuple`][trcks.AwaitableResultTuple].

    The number of side effect outputs determines how many times each original
    element is repeated in the resulting tuple.

    [`AwaitableFailure`][trcks.AwaitableFailure] values are passed on without side
    effects.

    Args:
        callable_: Synchronous side effect to apply to each success element.
        *args:
            Positional arguments to be passed to `callable_`.
        **kwargs:
            Keyword arguments to be passed to `callable_`.

    Returns:
        Applies the given side effect and returns an
            [`AwaitableResultTuple`][trcks.AwaitableResultTuple] where each original
            success element is repeated once per element returned by the side effect.

    Examples:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> def _log_twice(n: int) -> tuple[None, None]:
        ...     return print(f"Received: {n}"), print(f"Received: {n}")
        ...
        >>> log_twice = art.tap_successes_to_iterable(_log_twice)
        >>> a_r_tpl = log_twice(art.construct_successes_from_iterable((7,)))
        >>> r_tpl = asyncio.run(art.to_coroutine_result_tuple(a_r_tpl))
        Received: 7
        Received: 7
        >>> r_tpl
        ('success', (7, 7))
    """
    return a.map_(rt.tap_successes_to_iterable(callable_, *args, **kwargs))


def tap_successes_to_result(
    callable_: Callable[Concatenate[_S1, _P], Result[_F2, object]],
    /,
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[
    [AwaitableResultTuple[_F1, _S1]],
    AwaitableResultTuple[_F1 | _F2, _S1],
]:
    """Apply a synchronous side effect with return type [`Result`][trcks.Result]
    to each element in an [`AwaitableResultTuple`][trcks.AwaitableResultTuple].

    [`AwaitableFailure`][trcks.AwaitableFailure] values are passed on without side
    effects.

    Args:
        callable_: Synchronous side effect to apply to each success element.
        *args:
            Positional arguments to be passed to `callable_`.
        **kwargs:
            Keyword arguments to be passed to `callable_`.

    Returns:
        Applies the given side effect to each success element.
            If the given side effect returns a [`Failure`][trcks.Failure],
            *this* [`Failure`][trcks.Failure] is returned.
            If the given side effect returns a [`Success`][trcks.Success],
            *the original* success element is returned.

    Examples:
        >>> import asyncio
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> def _validate_positive(n: int) -> Result[str, None]:
        ...     if n <= 0:
        ...         return "failure", "negative"
        ...     return "success", None
        ...
        >>> validate_positive = art.tap_successes_to_result(_validate_positive)
        >>> a_r_tpl_1 = validate_positive(art.construct_successes_from_iterable((1, 2)))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('success', (1, 2))
        >>> a_r_tpl_2 = validate_positive(
        ...     art.construct_successes_from_iterable((1, -1))
        ... )
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('failure', 'negative')
        >>> a_r_tpl_3 = validate_positive(art.construct_failure("oops"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_3))
        ('failure', 'oops')
    """
    return a.map_(rt.tap_successes_to_result(callable_, *args, **kwargs))


def tap_successes_to_result_iterable(
    callable_: Callable[Concatenate[_S1, _P], ResultIterable[_F2, object]],
    /,
    *args: _P.args,
    **kwargs: _P.kwargs,
) -> Callable[
    [AwaitableResultTuple[_F1, _S1]],
    AwaitableResultTuple[_F1 | _F2, _S1],
]:
    """Apply a synchronous side effect with return type
    [`ResultIterable`][trcks.ResultIterable] to each element in an
    [`AwaitableResultTuple`][trcks.AwaitableResultTuple].

    [`AwaitableFailure`][trcks.AwaitableFailure] values are passed on without side
    effects.

    Args:
        callable_: Synchronous side effect to apply to each success element.
        *args:
            Positional arguments to be passed to `callable_`.
        **kwargs:
            Keyword arguments to be passed to `callable_`.

    Returns:
        Applies the given side effect to each success element.
            If the given side effect returns a [`Failure`][trcks.Failure], *this*
            [`Failure`][trcks.Failure] is returned. If the given side effect returns a
            [`SuccessIterable`][trcks.SuccessIterable], *the original* success element
            is repeated once per element in the success iterable.

    Examples:
        >>> import asyncio
        >>> from trcks import ResultTuple
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> def _validate_positive_twice(n: int) -> ResultTuple[str, None]:
        ...     if n <= 0:
        ...         return "failure", "negative"
        ...     return "success", (None, None)
        ...
        >>> validate_positive_twice = art.tap_successes_to_result_iterable(
        ...     _validate_positive_twice
        ... )
        >>> a_r_tpl_1 = validate_positive_twice(
        ...     art.construct_successes_from_iterable((7,))
        ... )
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_1))
        ('success', (7, 7))
        >>> a_r_tpl_2 = validate_positive_twice(
        ...     art.construct_successes_from_iterable((1, -1))
        ... )
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_2))
        ('failure', 'negative')
        >>> a_r_tpl_3 = validate_positive_twice(art.construct_failure("oops"))
        >>> asyncio.run(art.to_coroutine_result_tuple(a_r_tpl_3))
        ('failure', 'oops')
    """
    return a.map_(rt.tap_successes_to_result_iterable(callable_, *args, **kwargs))


async def to_coroutine_result_tuple(
    a_r_tpl: AwaitableResultTuple[_F, _S],
    /,
) -> ResultTuple[_F, _S]:
    """Turn an [`AwaitableResultTuple`][trcks.AwaitableResultTuple] into a
    [`Coroutine`][collections.abc.Coroutine].

    This is useful for functions that expect a coroutine
    (e.g. [`run`][asyncio.run] in Python 3.13 and older).

    Args:
        a_r_tpl: The [`AwaitableResultTuple`][trcks.AwaitableResultTuple] to be
            transformed into a [`Coroutine`][collections.abc.Coroutine].

    Returns:
        The given [`AwaitableResultTuple`][trcks.AwaitableResultTuple] transformed
            into a [`Coroutine`][collections.abc.Coroutine].

    Examples:
        >>> import asyncio
        >>> from trcks import ResultTuple
        >>> from trcks.fp.monads import awaitable_result_tuple as art
        >>> loop = asyncio.new_event_loop()
        >>> future: asyncio.Future[ResultTuple[str, int]] = loop.create_future()
        >>> future.set_result(("success", (1, 2)))
        >>> future
        <Future finished result=('success', (1, 2))>
        >>> coro = art.to_coroutine_result_tuple(future)
        >>> coro
        <coroutine object to_coroutine_result_tuple at 0x...>
        >>> loop.run_until_complete(coro)
        ('success', (1, 2))
        >>> loop.close()
    """
    return await a_r_tpl
