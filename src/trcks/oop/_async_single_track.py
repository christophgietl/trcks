from __future__ import annotations

import dataclasses
from collections.abc import Awaitable
from typing import TYPE_CHECKING, TypeVar

from trcks.fp.monad import awaitable
from trcks.oop._async_dual_track import AsyncDualTrack, AwaitableResult
from trcks.oop._track import Track

if TYPE_CHECKING:
    from collections.abc import Callable

    from trcks.oop._dual_track import Result


_F = TypeVar("_F")
_S = TypeVar("_S")
_T = TypeVar("_T")

_T_co = TypeVar("_T_co", covariant=True)


@dataclasses.dataclass(frozen=True)
class AsyncSingleTrack(Track[Awaitable[_T_co]]):
    @staticmethod
    def construct(value: _T) -> AsyncSingleTrack[_T]:
        return AsyncSingleTrack(awaitable.construct(value))

    @staticmethod
    def construct_from_awaitable(awtbl: Awaitable[_T]) -> AsyncSingleTrack[_T]:
        return AsyncSingleTrack(awtbl)

    def map(self, f: Callable[[_T_co], _T]) -> AsyncSingleTrack[_T]:
        f_mapped = awaitable.map_(f)
        return AsyncSingleTrack(f_mapped(self.core))

    def map_to_awaitable(
        self, f: Callable[[_T_co], Awaitable[_T]]
    ) -> AsyncSingleTrack[_T]:
        f_mapped = awaitable.map_to_awaitable(f)
        return AsyncSingleTrack(f_mapped(self.core))

    def map_to_awaitable_result(
        self, f: Callable[[_T_co], AwaitableResult[_F, _S]]
    ) -> AsyncDualTrack[_F, _S]:
        return AsyncDualTrack.construct_success_from_awaitable(
            self.core
        ).map_sucess_to_awaitable_result(f)

    def map_to_result(
        self, f: Callable[[_T_co], Result[_F, _S]]
    ) -> AsyncDualTrack[_F, _S]:
        return AsyncDualTrack.construct_success_from_awaitable(
            self.core
        ).map_sucess_to_result(f)
