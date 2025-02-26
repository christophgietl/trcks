from __future__ import annotations

import dataclasses
import sys
from typing import TYPE_CHECKING, Literal, TypeVar

from trcks.fp.monad import awaitable_result, result
from trcks.oop._track import Track
from trcks.oop.async_dual_track import AsyncDualTrack, AwaitableResult

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

if sys.version_info >= (3, 11):
    from typing import Never, TypeAlias
else:
    from typing_extensions import Never, TypeAlias

_F = TypeVar("_F")
_S = TypeVar("_S")

_F_co = TypeVar("_F_co", covariant=True)
_S_co = TypeVar("_S_co", covariant=True)

Result: TypeAlias = result.Result[_F_co, _S_co]


@dataclasses.dataclass(frozen=True)
class DualTrack(Track[Result[_F_co, _S_co]]):
    @property
    async def _core_as_awaitable_result(self) -> Result[_F_co, _S_co]:
        return self.core

    @staticmethod
    def construct_failure(value: _F) -> DualTrack[_F, Never]:
        return DualTrack(result.of_failure(value))

    @staticmethod
    def construct_from_result(rslt: Result[_F, _S]) -> DualTrack[_F, _S]:
        return DualTrack(rslt)

    @staticmethod
    def construct_success(value: _S) -> DualTrack[Never, _S]:
        return DualTrack(result.of_success(value))

    def map_failure(self, f: Callable[[_F_co], _F]) -> DualTrack[_F, _S_co]:
        f_mapped = result.map_failure(f)
        return DualTrack(f_mapped(self.core))

    def map_failure_to_awaitable(
        self, f: Callable[[_F_co], Awaitable[_F]]
    ) -> AsyncDualTrack[_F, _S_co]:
        f_mapped = awaitable_result.map_failure_to_awaitable(f)
        return AsyncDualTrack(f_mapped(self._core_as_awaitable_result))

    def map_failure_to_awaitable_result(
        self, f: Callable[[_F_co], AwaitableResult[_F, _S]]
    ) -> AsyncDualTrack[_F, _S_co | _S]:
        f_mapped = awaitable_result.map_failure_to_awaitable_result(f)
        return AsyncDualTrack(f_mapped(self._core_as_awaitable_result))

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
        f_mapped = awaitable_result.map_success_to_awaitable(f)
        return AsyncDualTrack(f_mapped(self._core_as_awaitable_result))

    def map_success_to_awaitable_result(
        self, f: Callable[[_S_co], AwaitableResult[_F, _S]]
    ) -> AsyncDualTrack[_F_co | _F, _S]:
        f_mapped = awaitable_result.map_success_to_awaitable_result(f)
        return AsyncDualTrack(f_mapped(self._core_as_awaitable_result))

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
