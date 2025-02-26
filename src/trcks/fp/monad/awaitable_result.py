from __future__ import annotations

import sys
from collections.abc import Awaitable, Callable
from typing import TypeVar

from trcks.fp.monad import awaitable, result

if sys.version_info >= (3, 11):
    from typing import TypeAlias
else:
    from typing_extensions import TypeAlias


_F = TypeVar("_F")
_F1 = TypeVar("_F1")
_F2 = TypeVar("_F2")
_S = TypeVar("_S")
_S1 = TypeVar("_S1")
_S2 = TypeVar("_S2")

_F_co = TypeVar("_F_co", covariant=True)
_S_co = TypeVar("_S_co", covariant=True)

AwaitableFailure: TypeAlias = Awaitable[result.Failure[_F_co]]
AwaitableSuccess: TypeAlias = Awaitable[result.Success[_S_co]]
AwaitableResult: TypeAlias = Awaitable[result.Result[_F_co, _S_co]]


def construct_failure(value: _F) -> AwaitableFailure[_F]:
    return awaitable.construct(result.construct_failure(value))


construct_failure_from_awaitable = awaitable.map_(result.construct_failure)


def construct_from_result(rslt: result.Result[_F, _S]) -> AwaitableResult[_F, _S]:
    return awaitable.construct(rslt)


def construct_success(value: _S) -> AwaitableSuccess[_S]:
    return awaitable.construct(result.construct_success(value))


construct_success_from_awaitable = awaitable.map_(result.construct_success)


def map_failure(
    f: Callable[[_F1], _F2],
) -> Callable[[AwaitableResult[_F1, _S1]], AwaitableResult[_F2, _S1]]:
    return awaitable.map_(result.map_failure(f))


def map_failure_to_awaitable(
    f: Callable[[_F1], Awaitable[_F2]],
) -> Callable[[AwaitableResult[_F1, _S1]], AwaitableResult[_F2, _S1]]:
    async def mapped_f(
        a_rslt: AwaitableResult[_F1, _S1],
    ) -> result.Result[_F2, _S1]:
        rslt = await a_rslt
        if rslt[0] == "success":
            return rslt
        return result.construct_failure(await f(rslt[1]))

    return mapped_f


def map_failure_to_awaitable_result(
    f: Callable[[_F1], AwaitableResult[_F2, _S2]],
) -> Callable[[AwaitableResult[_F1, _S1]], AwaitableResult[_F2, _S1 | _S2]]:
    async def mapped_f(
        a_rslt: AwaitableResult[_F1, _S1],
    ) -> result.Result[_F2, _S1 | _S2]:
        rslt = await a_rslt
        if rslt[0] == "success":
            return rslt
        return await f(rslt[1])

    return mapped_f


def map_failure_to_result(
    f: Callable[[_F1], result.Result[_F2, _S2]],
) -> Callable[[AwaitableResult[_F1, _S1]], AwaitableResult[_F2, _S1 | _S2]]:
    async def mapped_f(
        a_rslt: AwaitableResult[_F1, _S1],
    ) -> result.Result[_F2, _S1 | _S2]:
        rslt = await a_rslt
        if rslt[0] == "success":
            return rslt
        return f(rslt[1])

    return mapped_f


def map_success(
    f: Callable[[_S1], _S2],
) -> Callable[[AwaitableResult[_F1, _S1]], AwaitableResult[_F1, _S2]]:
    return awaitable.map_(result.map_success(f))


def map_success_to_awaitable(
    f: Callable[[_S1], Awaitable[_S2]],
) -> Callable[[AwaitableResult[_F1, _S1]], AwaitableResult[_F1, _S2]]:
    async def mapped_f(
        a_rslt: AwaitableResult[_F1, _S1],
    ) -> result.Result[_F1, _S2]:
        rslt = await a_rslt
        if rslt[0] == "failure":
            return rslt
        return result.construct_success(await f(rslt[1]))

    return mapped_f


def map_success_to_awaitable_result(
    f: Callable[[_S1], AwaitableResult[_F2, _S2]],
) -> Callable[[AwaitableResult[_F1, _S1]], AwaitableResult[_F1 | _F2, _S2]]:
    async def mapped_f(
        a_rslt: AwaitableResult[_F1, _S1],
    ) -> result.Result[_F1 | _F2, _S2]:
        rslt = await a_rslt
        if rslt[0] == "failure":
            return rslt
        return await f(rslt[1])

    return mapped_f


def map_success_to_result(
    f: Callable[[_S1], result.Result[_F2, _S2]],
) -> Callable[[AwaitableResult[_F1, _S1]], AwaitableResult[_F1 | _F2, _S2]]:
    async def mapped_f(
        a_rslt: AwaitableResult[_F1, _S1],
    ) -> result.Result[_F1 | _F2, _S2]:
        rslt = await a_rslt
        if rslt[0] == "failure":
            return rslt
        return f(rslt[1])

    return mapped_f
