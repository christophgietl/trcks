from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING, Literal

from trcks._typing_extensions import Never, TypeAlias, TypeVar
from trcks.fp.monad import result
from trcks.oop._async_dual_track import AsyncDualTrack, AwaitableResult
from trcks.oop._track import Track

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable


_F = TypeVar("_F")
_S = TypeVar("_S")

_F_co = TypeVar("_F_co", covariant=True, default=Never)
_S_co = TypeVar("_S_co", covariant=True, default=Never)

Result: TypeAlias = result.Result[_F_co, _S_co]


@dataclasses.dataclass(frozen=True)
class DualTrack(Track[Result[_F_co, _S_co]]):
    @staticmethod
    def construct_failure(value: _F) -> DualTrack[_F, Never]:
        return DualTrack(result.construct_failure(value))

    @staticmethod
    def construct_from_result(rslt: Result[_F, _S]) -> DualTrack[_F, _S]:
        return DualTrack(rslt)

    @staticmethod
    def construct_success(value: _S) -> DualTrack[Never, _S]:
        return DualTrack(result.construct_success(value))

    def map_failure(self, f: Callable[[_F_co], _F]) -> DualTrack[_F, _S_co]:
        f_mapped = result.map_failure(f)
        return DualTrack(f_mapped(self.core))

    def map_failure_to_awaitable(
        self, f: Callable[[_F_co], Awaitable[_F]]
    ) -> AsyncDualTrack[_F, _S_co]:
        return AsyncDualTrack.construct_from_result(self.core).map_failure_to_awaitable(
            f
        )

    def map_failure_to_awaitable_result(
        self, f: Callable[[_F_co], AwaitableResult[_F, _S]]
    ) -> AsyncDualTrack[_F, _S_co | _S]:
        return AsyncDualTrack.construct_from_result(
            self.core
        ).map_failure_to_awaitable_result(f)

    def map_failure_to_result(
        self, f: Callable[[_F_co], Result[_F, _S]]
    ) -> DualTrack[_F, _S_co | _S]:
        f_mapped = result.map_failure_to_result(f)
        return DualTrack(f_mapped(self.core))

    def map_success(self, f: Callable[[_S_co], _S]) -> DualTrack[_F_co, _S]:
        f_mapped = result.map_success(f)
        return DualTrack(f_mapped(self.core))

    def map_success_to_awaitable(
        self, f: Callable[[_S_co], Awaitable[_S]]
    ) -> AsyncDualTrack[_F_co, _S]:
        return AsyncDualTrack.construct_from_result(self.core).map_sucess_to_awaitable(
            f
        )

    def map_success_to_awaitable_result(
        self, f: Callable[[_S_co], AwaitableResult[_F, _S]]
    ) -> AsyncDualTrack[_F_co | _F, _S]:
        return AsyncDualTrack.construct_from_result(
            self.core
        ).map_sucess_to_awaitable_result(f)

    def map_success_to_result(
        self, f: Callable[[_S_co], Result[_F, _S]]
    ) -> DualTrack[_F_co | _F, _S]:
        f_mapped = result.map_success_to_result(f)
        return DualTrack(f_mapped(self.core))

    @property
    def track(self) -> Literal["failure", "success"]:
        return self.core[0]

    @property
    def value(self) -> _F_co | _S_co:
        return self.core[1]
