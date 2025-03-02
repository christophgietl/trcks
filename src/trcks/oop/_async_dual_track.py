from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING, Literal

from trcks._typing_extensions import Never, TypeVar
from trcks.fp.monad import awaitable_result
from trcks.fp.monad.awaitable_result import (
    AwaitableFailure,
    AwaitableResult,
    AwaitableSuccess,
)
from trcks.oop._track import Track

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Awaitable, Callable

    from trcks.oop._dual_track import Result


_F = TypeVar("_F")
_S = TypeVar("_S")

_F_co = TypeVar("_F_co", covariant=True, default=Never)
_S_co = TypeVar("_S_co", covariant=True, default=Never)


@dataclasses.dataclass(frozen=True)
class AsyncDualTrack(Track[AwaitableResult[_F_co, _S_co]]):
    @staticmethod
    def construct_failure(value: _F) -> AsyncDualTrack[_F, Never]:
        return AsyncDualTrack(awaitable_result.construct_failure(value))

    @staticmethod
    def construct_failure_from_awaitable(
        awtbl: Awaitable[_F],
    ) -> AsyncDualTrack[_F, Never]:
        return AsyncDualTrack(awaitable_result.construct_failure_from_awaitable(awtbl))

    @staticmethod
    def construct_from_awaitable_result(
        a_rslt: AwaitableResult[_F, _S],
    ) -> AsyncDualTrack[_F, _S]:
        return AsyncDualTrack(a_rslt)

    @staticmethod
    def construct_from_result(rslt: Result[_F, _S]) -> AsyncDualTrack[_F, _S]:
        return AsyncDualTrack(awaitable_result.construct_from_result(rslt))

    @staticmethod
    def construct_success(value: _S) -> AsyncDualTrack[Never, _S]:
        return AsyncDualTrack(awaitable_result.construct_success(value))

    @staticmethod
    def construct_success_from_awaitable(
        awtbl: Awaitable[_S],
    ) -> AsyncDualTrack[Never, _S]:
        return AsyncDualTrack(awaitable_result.construct_success_from_awaitable(awtbl))

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

    def map_success_to_awaitable(
        self, f: Callable[[_S_co], Awaitable[_S]]
    ) -> AsyncDualTrack[_F_co, _S]:
        f_mapped = awaitable_result.map_success_to_awaitable(f)
        return AsyncDualTrack(f_mapped(self.core))

    def map_success_to_awaitable_result(
        self, f: Callable[[_S_co], AwaitableResult[_F, _S]]
    ) -> AsyncDualTrack[_F_co | _F, _S]:
        f_mapped = awaitable_result.map_success_to_awaitable_result(f)
        return AsyncDualTrack(f_mapped(self.core))

    def map_success_to_result(
        self, f: Callable[[_S_co], Result[_F, _S]]
    ) -> AsyncDualTrack[_F_co | _F, _S]:
        f_mapped = awaitable_result.map_success_to_result(f)
        return AsyncDualTrack(f_mapped(self.core))

    @property
    async def track(self) -> Literal["failure", "success"]:
        return (await self.core)[0]

    @property
    async def value(self) -> _F_co | _S_co:
        return (await self.core)[1]


__all__ = ["AsyncDualTrack", "AwaitableFailure", "AwaitableResult", "AwaitableSuccess"]
