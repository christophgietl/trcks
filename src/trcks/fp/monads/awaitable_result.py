from __future__ import annotations

from typing import TYPE_CHECKING

from trcks._typing import TypeVar, assert_never
from trcks.fp.monads import awaitable, result

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Awaitable, Callable

    from trcks._type_aliases import (
        AwaitableFailure,
        AwaitableResult,
        AwaitableSuccess,
        Result,
    )

_F = TypeVar("_F")
_F1 = TypeVar("_F1")
_F2 = TypeVar("_F2")
_S = TypeVar("_S")
_S1 = TypeVar("_S1")
_S2 = TypeVar("_S2")


def construct_failure(value: _F) -> AwaitableFailure[_F]:
    return awaitable.construct(result.construct_failure(value))


def construct_failure_from_awaitable(awtbl: Awaitable[_F]) -> AwaitableFailure[_F]:
    return awaitable.map_(result.construct_failure)(awtbl)


def construct_from_result(rslt: Result[_F, _S]) -> AwaitableResult[_F, _S]:
    return awaitable.construct(rslt)


def construct_success(value: _S) -> AwaitableSuccess[_S]:
    return awaitable.construct(result.construct_success(value))


def construct_success_from_awaitable(awtbl: Awaitable[_S]) -> AwaitableSuccess[_S]:
    return awaitable.map_(result.construct_success)(awtbl)


def map_failure(
    f: Callable[[_F1], _F2],
) -> Callable[[AwaitableResult[_F1, _S1]], AwaitableResult[_F2, _S1]]:
    return awaitable.map_(result.map_failure(f))


def map_failure_to_awaitable(
    f: Callable[[_F1], Awaitable[_F2]],
) -> Callable[[AwaitableResult[_F1, _S1]], AwaitableResult[_F2, _S1]]:
    def composed_f(value: _F1) -> AwaitableFailure[_F2]:
        return construct_failure_from_awaitable(f(value))

    return map_failure_to_awaitable_result(composed_f)


def map_failure_to_awaitable_result(
    f: Callable[[_F1], AwaitableResult[_F2, _S2]],
) -> Callable[[AwaitableResult[_F1, _S1]], AwaitableResult[_F2, _S1 | _S2]]:
    async def partially_mapped_f(rslt: Result[_F1, _S1]) -> Result[_F2, _S1 | _S2]:
        if rslt[0] == "failure":
            return await f(rslt[1])
        if rslt[0] == "success":
            return rslt
        return assert_never(rslt)  # type: ignore [unreachable]  # pragma: no cover

    return awaitable.map_to_awaitable(partially_mapped_f)


def map_failure_to_result(
    f: Callable[[_F1], Result[_F2, _S2]],
) -> Callable[[AwaitableResult[_F1, _S1]], AwaitableResult[_F2, _S1 | _S2]]:
    return awaitable.map_(result.map_failure_to_result(f))


def map_success(
    f: Callable[[_S1], _S2],
) -> Callable[[AwaitableResult[_F1, _S1]], AwaitableResult[_F1, _S2]]:
    return awaitable.map_(result.map_success(f))


def map_success_to_awaitable(
    f: Callable[[_S1], Awaitable[_S2]],
) -> Callable[[AwaitableResult[_F1, _S1]], AwaitableResult[_F1, _S2]]:
    def composed_f(value: _S1) -> AwaitableSuccess[_S2]:
        return construct_success_from_awaitable(f(value))

    return map_success_to_awaitable_result(composed_f)


def map_success_to_awaitable_result(
    f: Callable[[_S1], AwaitableResult[_F2, _S2]],
) -> Callable[[AwaitableResult[_F1, _S1]], AwaitableResult[_F1 | _F2, _S2]]:
    async def partially_mapped_f(rslt: Result[_F1, _S1]) -> Result[_F1 | _F2, _S2]:
        if rslt[0] == "failure":
            return rslt
        if rslt[0] == "success":
            return await f(rslt[1])
        return assert_never(rslt)  # type: ignore [unreachable]  # pragma: no cover

    return awaitable.map_to_awaitable(partially_mapped_f)


def map_success_to_result(
    f: Callable[[_S1], Result[_F2, _S2]],
) -> Callable[[AwaitableResult[_F1, _S1]], AwaitableResult[_F1 | _F2, _S2]]:
    return awaitable.map_(result.map_success_to_result(f))


__docformat__ = "google"
