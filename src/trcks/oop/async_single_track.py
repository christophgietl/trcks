from __future__ import annotations

import dataclasses
import sys
from collections.abc import Awaitable
from typing import TYPE_CHECKING, TypeVar

from trcks.fp.monad import awaitable, awaitable_result
from trcks.oop._track import Track
from trcks.oop.async_dual_track import AsyncDualTrack, AwaitableResult

if TYPE_CHECKING:
    from collections.abc import Callable

    from trcks.oop.dual_track import Result


if sys.version_info >= (3, 11):
    from typing import Never
else:
    from typing_extensions import Never


_F = TypeVar("_F")
_S = TypeVar("_S")
_T = TypeVar("_T")

_T_co = TypeVar("_T_co", covariant=True)


@dataclasses.dataclass(frozen=True)
class AsyncSingleTrack(Track[Awaitable[_T_co]]):
    @property
    def _core_as_awaitable_success(self) -> AwaitableResult[Never, _T_co]:
        return awaitable_result.construct_success_from_awaitable(self.core)

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
        f_mapped = awaitable_result.map_success_to_awaitable_result(f)
        return AsyncDualTrack(f_mapped(self._core_as_awaitable_success))

    def map_to_result(
        self, f: Callable[[_T_co], Result[_F, _S]]
    ) -> AsyncDualTrack[_F, _S]:
        f_mapped = awaitable_result.map_success_to_result(f)
        return AsyncDualTrack(f_mapped(self._core_as_awaitable_success))
