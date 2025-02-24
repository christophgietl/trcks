from __future__ import annotations

import sys
from collections.abc import Awaitable, Callable
from typing import TypeVar

from trcks.fp.monad import awaitable, dual_track

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

AwaitableDualTrack: TypeAlias = Awaitable[dual_track.DualTrack[_L_co, _R_co]]
AwaitableLeft: TypeAlias = Awaitable[dual_track.LeftTrack[_L_co]]
AwaitableRight: TypeAlias = Awaitable[dual_track.RightTrack[_R_co]]


def flat_map_left(
    f: Callable[[_L1], AwaitableDualTrack[_L2, _R2]],
) -> Callable[[AwaitableDualTrack[_L1, _R1]], AwaitableDualTrack[_L2, _R1 | _R2]]:
    async def mapped_f(
        adt: AwaitableDualTrack[_L1, _R1],
    ) -> dual_track.DualTrack[_L2, _R1 | _R2]:
        dt = await adt
        return await f(dt[1]) if dt[0] == "left" else dt

    return mapped_f


def flat_map_right(
    f: Callable[[_R1], AwaitableDualTrack[_L2, _R2]],
) -> Callable[[AwaitableDualTrack[_L1, _R1]], AwaitableDualTrack[_L1 | _L2, _R2]]:
    async def mapped_f(
        adt: AwaitableDualTrack[_L1, _R1],
    ) -> dual_track.DualTrack[_L1 | _L2, _R2]:
        dt = await adt
        return await f(dt[1]) if dt[0] == "right" else dt

    return mapped_f


from_awaitable_left = awaitable.map_(dual_track.of_left)
from_awaitable_right = awaitable.map_(dual_track.of_right)


def map_left(
    f: Callable[[_L1], _L2],
) -> Callable[[AwaitableDualTrack[_L1, _R1]], AwaitableDualTrack[_L2, _R1]]:
    return awaitable.map_(dual_track.map_left(f))


def map_right(
    f: Callable[[_R1], _R2],
) -> Callable[[AwaitableDualTrack[_L1, _R1]], AwaitableDualTrack[_L1, _R2]]:
    return awaitable.map_(dual_track.map_right(f))


def of_left(value: _L) -> AwaitableLeft[_L]:
    return awaitable.of(dual_track.of_left(value))


def of_right(value: _R) -> AwaitableRight[_R]:
    return awaitable.of(dual_track.of_right(value))
