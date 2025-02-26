from __future__ import annotations

import dataclasses
import sys
from typing import TYPE_CHECKING, Literal, TypeVar

from trcks.fp.monad import awaitable_result
from trcks.oop import _track

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from trcks.oop.dual_track import Result

if sys.version_info >= (3, 11):
    from typing import Never, TypeAlias
else:
    from typing_extensions import Never, TypeAlias

_F = TypeVar("_F")
_S = TypeVar("_S")

_F_co = TypeVar("_F_co", covariant=True)
_S_co = TypeVar("_S_co", covariant=True)


AwaitableResult: TypeAlias = awaitable_result.AwaitableResult[_F_co, _S_co]


@dataclasses.dataclass(frozen=True)
class AsyncDualTrack(_track.Track[AwaitableResult[_F_co, _S_co]]):
    @staticmethod
    def failure(value: Awaitable[_F]) -> AsyncDualTrack[_F, Never]:
        return AsyncDualTrack(awaitable_result.from_awaitable_failure(value))

    @staticmethod
    def failure_from_sync(value: _F) -> AsyncDualTrack[_F, Never]:
        return AsyncDualTrack(awaitable_result.of_failure(value))

    def map_failure(self, f: Callable[[_F_co], _F]) -> AsyncDualTrack[_F, _S_co]:
        f_mapped = awaitable_result.map_failure(f)
        return AsyncDualTrack(f_mapped(self.core))

    def map_failure_to_awaitable(
        self, f: Callable[[_F_co], Awaitable[_F]]
    ) -> AsyncDualTrack[_F, _S_co]:
        f_mapped = awaitable_result.map_failure_to_awaitable(f)
        return AsyncDualTrack(f_mapped(self.core))

    def map_failure_to_awaitable_result(
        self, f: Callable[[_F_co], AwaitableResult[_F, _S]]
    ) -> AsyncDualTrack[_F, _S_co | _S]:
        f_mapped = awaitable_result.map_failure_to_awaitable_result(f)
        return AsyncDualTrack(f_mapped(self.core))

    def map_failure_to_result(
        self, f: Callable[[_F_co], Result[_F, _S]]
    ) -> AsyncDualTrack[_F, _S_co | _S]:
        f_mapped = awaitable_result.map_failure_to_result(f)
        return AsyncDualTrack(f_mapped(self.core))

    def map_success(self, f: Callable[[_S_co], _S]) -> AsyncDualTrack[_F_co, _S]:
        f_mapped = awaitable_result.map_success(f)
        return AsyncDualTrack(f_mapped(self.core))

    def map_sucess_to_awaitable(
        self, f: Callable[[_S_co], Awaitable[_S]]
    ) -> AsyncDualTrack[_F_co, _S]:
        f_mapped = awaitable_result.map_success_to_awaitable(f)
        return AsyncDualTrack(f_mapped(self.core))

    def map_sucess_to_awaitable_result(
        self, f: Callable[[_S_co], AwaitableResult[_F, _S]]
    ) -> AsyncDualTrack[_F_co | _F, _S]:
        f_mapped = awaitable_result.map_success_to_awaitable_result(f)
        return AsyncDualTrack(f_mapped(self.core))

    def map_sucess_to_result(
        self, f: Callable[[_S_co], Result[_F, _S]]
    ) -> AsyncDualTrack[_F_co | _F, _S]:
        f_mapped = awaitable_result.map_success_to_result(f)
        return AsyncDualTrack(f_mapped(self.core))

    @staticmethod
    def success(value: Awaitable[_S]) -> AsyncDualTrack[Never, _S]:
        return AsyncDualTrack(awaitable_result.from_awaitable_success(value))

    @property
    async def track(self) -> Literal["failure", "success"]:
        return (await self.core)[0]

    @property
    async def value(self) -> _F_co | _S_co:
        return (await self.core)[1]
