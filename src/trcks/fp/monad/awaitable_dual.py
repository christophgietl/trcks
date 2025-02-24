from __future__ import annotations

import sys
from collections.abc import Awaitable, Callable
from typing import TypeVar

from trcks.fp.monad import awaitable, dual

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

AwaitableDual: TypeAlias = Awaitable[dual.Dual[_L_co, _R_co]]
AwaitableLeft: TypeAlias = Awaitable[dual.Left[_L_co]]
AwaitableRight: TypeAlias = Awaitable[dual.Right[_R_co]]


def flat_map_left(
    f: Callable[[_L1], AwaitableDual[_L2, _R2]],
) -> Callable[[AwaitableDual[_L1, _R1]], AwaitableDual[_L2, _R1 | _R2]]:
    async def mapped_f(
        adl: AwaitableDual[_L1, _R1],
    ) -> dual.Dual[_L2, _R1 | _R2]:
        dl = await adl
        return await f(dl[1]) if dl[0] == "left" else dl

    return mapped_f


def flat_map_right(
    f: Callable[[_R1], AwaitableDual[_L2, _R2]],
) -> Callable[[AwaitableDual[_L1, _R1]], AwaitableDual[_L1 | _L2, _R2]]:
    async def mapped_f(
        adl: AwaitableDual[_L1, _R1],
    ) -> dual.Dual[_L1 | _L2, _R2]:
        dl = await adl
        return await f(dl[1]) if dl[0] == "right" else dl

    return mapped_f


from_awaitable_left = awaitable.map_(dual.of_left)
from_awaitable_right = awaitable.map_(dual.of_right)


def map_left(
    f: Callable[[_L1], _L2],
) -> Callable[[AwaitableDual[_L1, _R1]], AwaitableDual[_L2, _R1]]:
    return awaitable.map_(dual.map_left(f))


def map_right(
    f: Callable[[_R1], _R2],
) -> Callable[[AwaitableDual[_L1, _R1]], AwaitableDual[_L1, _R2]]:
    return awaitable.map_(dual.map_right(f))


def of_left(value: _L) -> AwaitableLeft[_L]:
    return awaitable.of(dual.of_left(value))


def of_right(value: _R) -> AwaitableRight[_R]:
    return awaitable.of(dual.of_right(value))
