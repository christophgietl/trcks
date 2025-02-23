from __future__ import annotations

import sys
from collections.abc import Awaitable, Callable
from typing import TypeVar

from trcks.fp.monad import awaitable, either

if sys.version_info >= (3, 11):
    from typing import TypeAlias
else:
    from typing_extensions import TypeAlias


_L = TypeVar("_L")
_L1 = TypeVar("_L1")
_L2 = TypeVar("_L2")
_R = TypeVar("_R")
_R1 = TypeVar("_R1")
_R2 = TypeVar("_R2")

_L_co = TypeVar("_L_co", covariant=True)
_R_co = TypeVar("_R_co", covariant=True)

AwaitableEither: TypeAlias = Awaitable[either.Either[_L_co, _R_co]]
AwaitableLeft: TypeAlias = Awaitable[either.Left[_L_co]]
AwaitableRight: TypeAlias = Awaitable[either.Right[_R_co]]


def flat_map_left(
    f: Callable[[_L1], AwaitableEither[_L2, _R2]],
) -> Callable[[AwaitableEither[_L1, _R1]], AwaitableEither[_L2, _R1 | _R2]]:
    async def mapped_f(
        aw_ethr: AwaitableEither[_L1, _R1],
    ) -> either.Either[_L2, _R1 | _R2]:
        ethr = await aw_ethr
        return await f(ethr[1]) if ethr[0] == "left" else ethr

    return mapped_f


def flat_map_right(
    f: Callable[[_R1], AwaitableEither[_L2, _R2]],
) -> Callable[[AwaitableEither[_L1, _R1]], AwaitableEither[_L1 | _L2, _R2]]:
    async def mapped_f(
        aw_ethr: AwaitableEither[_L1, _R1],
    ) -> either.Either[_L1 | _L2, _R2]:
        ethr = await aw_ethr
        return await f(ethr[1]) if ethr[0] == "right" else ethr

    return mapped_f


from_awaitable_left = awaitable.map_(either.of_left)
from_awaitable_right = awaitable.map_(either.of_right)


def map_left(
    f: Callable[[_L1], _L2],
) -> Callable[[AwaitableEither[_L1, _R1]], AwaitableEither[_L2, _R1]]:
    return awaitable.map_(either.map_left(f))


def map_right(
    f: Callable[[_R1], _R2],
) -> Callable[[AwaitableEither[_L1, _R1]], AwaitableEither[_L1, _R2]]:
    return awaitable.map_(either.map_right(f))


def of_left(value: _L) -> AwaitableLeft[_L]:
    return awaitable.of(either.of_left(value))


def of_right(value: _R) -> AwaitableRight[_R]:
    return awaitable.of(either.of_right(value))
