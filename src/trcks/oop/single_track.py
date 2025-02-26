from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING, TypeVar

from trcks.oop._track import Track
from trcks.oop.async_dual_track import AsyncDualTrack, AwaitableResult
from trcks.oop.async_single_track import AsyncSingleTrack
from trcks.oop.dual_track import DualTrack, Result

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

_F = TypeVar("_F")
_S = TypeVar("_S")
_T = TypeVar("_T")

_T_co = TypeVar("_T_co", covariant=True)


@dataclasses.dataclass(frozen=True)
class SingleTrack(Track[_T_co]):
    def map(self, f: Callable[[_T_co], _T]) -> SingleTrack[_T]:
        return SingleTrack(f(self.core))

    def map_to_awaitable(
        self, f: Callable[[_T_co], Awaitable[_T]]
    ) -> AsyncSingleTrack[_T]:
        return AsyncSingleTrack(f(self.core))

    def map_to_awaitable_result(
        self, f: Callable[[_T_co], AwaitableResult[_F, _S]]
    ) -> AsyncDualTrack[_F, _S]:
        return AsyncDualTrack(f(self.core))

    def map_to_result(self, f: Callable[[_T_co], Result[_F, _S]]) -> DualTrack[_F, _S]:
        return DualTrack(f(self.core))
