from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING, Literal

from trcks import AwaitableResult, Result
from trcks._typing import Never, TypeVar
from trcks.fp.monads import result
from trcks.oop._awaitable_result_railway import AwaitableResultRailway
from trcks.oop._base_railway import BaseRailway

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Awaitable, Callable


_F = TypeVar("_F")
_S = TypeVar("_S")

_F_co = TypeVar("_F_co", covariant=True, default=Never)
_S_co = TypeVar("_S_co", covariant=True, default=Never)


@dataclasses.dataclass(frozen=True)
class ResultRailway(BaseRailway[Result[_F_co, _S_co]]):
    @staticmethod
    def construct_failure(value: _F) -> ResultRailway[_F, Never]:
        return ResultRailway(result.construct_failure(value))

    @staticmethod
    def construct_from_result(rslt: Result[_F, _S]) -> ResultRailway[_F, _S]:
        return ResultRailway(rslt)

    @staticmethod
    def construct_success(value: _S) -> ResultRailway[Never, _S]:
        return ResultRailway(result.construct_success(value))

    def map_failure(self, f: Callable[[_F_co], _F]) -> ResultRailway[_F, _S_co]:
        f_mapped = result.map_failure(f)
        return ResultRailway(f_mapped(self.core))

    def map_failure_to_awaitable(
        self, f: Callable[[_F_co], Awaitable[_F]]
    ) -> AwaitableResultRailway[_F, _S_co]:
        return AwaitableResultRailway.construct_from_result(
            self.core
        ).map_failure_to_awaitable(f)

    def map_failure_to_awaitable_result(
        self, f: Callable[[_F_co], AwaitableResult[_F, _S]]
    ) -> AwaitableResultRailway[_F, _S_co | _S]:
        return AwaitableResultRailway.construct_from_result(
            self.core
        ).map_failure_to_awaitable_result(f)

    def map_failure_to_result(
        self, f: Callable[[_F_co], Result[_F, _S]]
    ) -> ResultRailway[_F, _S_co | _S]:
        f_mapped = result.map_failure_to_result(f)
        return ResultRailway(f_mapped(self.core))

    def map_success(self, f: Callable[[_S_co], _S]) -> ResultRailway[_F_co, _S]:
        f_mapped = result.map_success(f)
        return ResultRailway(f_mapped(self.core))

    def map_success_to_awaitable(
        self, f: Callable[[_S_co], Awaitable[_S]]
    ) -> AwaitableResultRailway[_F_co, _S]:
        return AwaitableResultRailway.construct_from_result(
            self.core
        ).map_success_to_awaitable(f)

    def map_success_to_awaitable_result(
        self, f: Callable[[_S_co], AwaitableResult[_F, _S]]
    ) -> AwaitableResultRailway[_F_co | _F, _S]:
        return AwaitableResultRailway.construct_from_result(
            self.core
        ).map_success_to_awaitable_result(f)

    def map_success_to_result(
        self, f: Callable[[_S_co], Result[_F, _S]]
    ) -> ResultRailway[_F_co | _F, _S]:
        f_mapped = result.map_success_to_result(f)
        return ResultRailway(f_mapped(self.core))

    @property
    def track(self) -> Literal["failure", "success"]:
        return self.core[0]

    @property
    def value(self) -> _F_co | _S_co:
        return self.core[1]


__docformat__ = "google"
