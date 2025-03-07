from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING

from trcks._typing import TypeVar
from trcks.oop._async_dual_track import AsyncDualTrack
from trcks.oop._async_single_track import AsyncSingleTrack
from trcks.oop._dual_track import DualTrack
from trcks.oop._track import Track

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Awaitable, Callable

    from trcks import AwaitableResult, Result

_F = TypeVar("_F")
_S = TypeVar("_S")
_T = TypeVar("_T")

_T_co = TypeVar("_T_co", covariant=True)


@dataclasses.dataclass(frozen=True)
class SingleTrack(Track[_T_co]):
    @staticmethod
    def construct(value: _T) -> SingleTrack[_T]:
        return SingleTrack(value)

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


__docformat__ = "google"
