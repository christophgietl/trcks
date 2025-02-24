from __future__ import annotations

import dataclasses
import sys
from typing import TYPE_CHECKING, Literal, TypeVar

from trcks.fp.monad import awaitable_dual_track
from trcks.oop import _track

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

if sys.version_info >= (3, 11):
    from typing import Never
else:
    from typing_extensions import Never

_L = TypeVar("_L")
_R = TypeVar("_R")

_L_co = TypeVar("_L_co", covariant=True)
_R_co = TypeVar("_R_co", covariant=True)


@dataclasses.dataclass(frozen=True)
class AwaitableDualTrackHelper(
    _track.TrackHelper[awaitable_dual_track.AwaitableDualTrack[_L_co, _R_co]]
):
    @staticmethod
    def left(value: Awaitable[_L]) -> AwaitableDualTrackHelper[_L, Never]:
        return AwaitableDualTrackHelper(awaitable_dual_track.from_awaitable_left(value))

    @staticmethod
    def left_from_sync(value: _L) -> AwaitableDualTrackHelper[_L, Never]:
        return AwaitableDualTrackHelper(awaitable_dual_track.of_left(value))

    def map_left(self, f: Callable[[_L_co], _L]) -> AwaitableDualTrackHelper[_L, _R_co]:
        f_mapped = awaitable_dual_track.map_left(f)
        return AwaitableDualTrackHelper(f_mapped(self.core))

    def map_left_to_async_dual_track(
        self, f: Callable[[_L_co], AwaitableDualTrackHelper[_L, _R]]
    ) -> AwaitableDualTrackHelper[_L, _R_co | _R]:
        f_unwrapped = AwaitableDualTrackHelper.unwrap_return_value(f)
        f_mapped = awaitable_dual_track.flat_map_left(f_unwrapped)
        return AwaitableDualTrackHelper(f_mapped(self.core))

    def map_right(
        self, f: Callable[[_R_co], _R]
    ) -> AwaitableDualTrackHelper[_L_co, _R]:
        f_mapped = awaitable_dual_track.map_right(f)
        return AwaitableDualTrackHelper(f_mapped(self.core))

    def map_right_to_async_dual_track(
        self, f: Callable[[_R_co], AwaitableDualTrackHelper[_L, _R]]
    ) -> AwaitableDualTrackHelper[_L_co | _L, _R]:
        f_unwrapped = AwaitableDualTrackHelper.unwrap_return_value(f)
        f_mapped = awaitable_dual_track.flat_map_right(f_unwrapped)
        return AwaitableDualTrackHelper(f_mapped(self.core))

    @staticmethod
    def right(value: Awaitable[_R]) -> AwaitableDualTrackHelper[Never, _R]:
        return AwaitableDualTrackHelper(
            awaitable_dual_track.from_awaitable_right(value)
        )

    @property
    async def track(self) -> Literal["left", "right"]:
        return (await self.core)[0]

    @property
    async def value(self) -> _L_co | _R_co:
        return (await self.core)[1]
