from __future__ import annotations

import dataclasses
import sys
from typing import TYPE_CHECKING, Literal, TypeVar

from trcks.fp.monad import awaitable_dual
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
class AsyncDualTrack(_track.Track[awaitable_dual.AwaitableDual[_L_co, _R_co]]):
    @staticmethod
    def left(value: Awaitable[_L]) -> AsyncDualTrack[_L, Never]:
        return AsyncDualTrack(awaitable_dual.from_awaitable_left(value))

    @staticmethod
    def left_from_sync(value: _L) -> AsyncDualTrack[_L, Never]:
        return AsyncDualTrack(awaitable_dual.of_left(value))

    def map_left(self, f: Callable[[_L_co], _L]) -> AsyncDualTrack[_L, _R_co]:
        f_mapped = awaitable_dual.map_left(f)
        return AsyncDualTrack(f_mapped(self.core))

    def map_left_to_async_dual_track(
        self, f: Callable[[_L_co], AsyncDualTrack[_L, _R]]
    ) -> AsyncDualTrack[_L, _R_co | _R]:
        f_unwrapped = AsyncDualTrack.unwrap_return_value(f)
        f_mapped = awaitable_dual.flat_map_left(f_unwrapped)
        return AsyncDualTrack(f_mapped(self.core))

    def map_right(self, f: Callable[[_R_co], _R]) -> AsyncDualTrack[_L_co, _R]:
        f_mapped = awaitable_dual.map_right(f)
        return AsyncDualTrack(f_mapped(self.core))

    def map_right_to_async_dual_track(
        self, f: Callable[[_R_co], AsyncDualTrack[_L, _R]]
    ) -> AsyncDualTrack[_L_co | _L, _R]:
        f_unwrapped = AsyncDualTrack.unwrap_return_value(f)
        f_mapped = awaitable_dual.flat_map_right(f_unwrapped)
        return AsyncDualTrack(f_mapped(self.core))

    @staticmethod
    def right(value: Awaitable[_R]) -> AsyncDualTrack[Never, _R]:
        return AsyncDualTrack(awaitable_dual.from_awaitable_right(value))

    @property
    async def track(self) -> Literal["left", "right"]:
        return (await self.core)[0]

    @property
    async def value(self) -> _L_co | _R_co:
        return (await self.core)[1]
