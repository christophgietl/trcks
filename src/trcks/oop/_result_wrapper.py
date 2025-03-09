from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING, Literal

from trcks import AwaitableResult, Result
from trcks._typing import Never, TypeVar
from trcks.fp.monads import result
from trcks.oop._awaitable_result_wrapper import AwaitableResultWrapper
from trcks.oop._base_wrapper import BaseWrapper

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Awaitable, Callable


_F = TypeVar("_F")
_S = TypeVar("_S")

_F_co = TypeVar("_F_co", covariant=True, default=Never)
_S_co = TypeVar("_S_co", covariant=True, default=Never)


@dataclasses.dataclass(frozen=True)
class ResultWrapper(BaseWrapper[Result[_F_co, _S_co]]):
    @staticmethod
    def construct_failure(value: _F) -> ResultWrapper[_F, Never]:
        return ResultWrapper(result.construct_failure(value))

    @staticmethod
    def construct_from_result(rslt: Result[_F, _S]) -> ResultWrapper[_F, _S]:
        return ResultWrapper(rslt)

    @staticmethod
    def construct_success(value: _S) -> ResultWrapper[Never, _S]:
        return ResultWrapper(result.construct_success(value))

    def map_failure(self, f: Callable[[_F_co], _F]) -> ResultWrapper[_F, _S_co]:
        f_mapped = result.map_failure(f)
        return ResultWrapper(f_mapped(self.core))

    def map_failure_to_awaitable(
        self, f: Callable[[_F_co], Awaitable[_F]]
    ) -> AwaitableResultWrapper[_F, _S_co]:
        return AwaitableResultWrapper.construct_from_result(
            self.core
        ).map_failure_to_awaitable(f)

    def map_failure_to_awaitable_result(
        self, f: Callable[[_F_co], AwaitableResult[_F, _S]]
    ) -> AwaitableResultWrapper[_F, _S_co | _S]:
        return AwaitableResultWrapper.construct_from_result(
            self.core
        ).map_failure_to_awaitable_result(f)

    def map_failure_to_result(
        self, f: Callable[[_F_co], Result[_F, _S]]
    ) -> ResultWrapper[_F, _S_co | _S]:
        f_mapped = result.map_failure_to_result(f)
        return ResultWrapper(f_mapped(self.core))

    def map_success(self, f: Callable[[_S_co], _S]) -> ResultWrapper[_F_co, _S]:
        f_mapped = result.map_success(f)
        return ResultWrapper(f_mapped(self.core))

    def map_success_to_awaitable(
        self, f: Callable[[_S_co], Awaitable[_S]]
    ) -> AwaitableResultWrapper[_F_co, _S]:
        return AwaitableResultWrapper.construct_from_result(
            self.core
        ).map_success_to_awaitable(f)

    def map_success_to_awaitable_result(
        self, f: Callable[[_S_co], AwaitableResult[_F, _S]]
    ) -> AwaitableResultWrapper[_F_co | _F, _S]:
        return AwaitableResultWrapper.construct_from_result(
            self.core
        ).map_success_to_awaitable_result(f)

    def map_success_to_result(
        self, f: Callable[[_S_co], Result[_F, _S]]
    ) -> ResultWrapper[_F_co | _F, _S]:
        f_mapped = result.map_success_to_result(f)
        return ResultWrapper(f_mapped(self.core))

    @property
    def track(self) -> Literal["failure", "success"]:
        return self.core[0]

    @property
    def value(self) -> _F_co | _S_co:
        return self.core[1]


__docformat__ = "google"
