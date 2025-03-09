from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING, Literal

from trcks import AwaitableResult, Result
from trcks._typing import Never, TypeVar
from trcks.fp.monads import awaitable_result
from trcks.oop._base_awaitable_wrapper import BaseAwaitableWrapper

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Awaitable, Callable


_F = TypeVar("_F")
_S = TypeVar("_S")

_F_co = TypeVar("_F_co", covariant=True, default=Never)
_S_co = TypeVar("_S_co", covariant=True, default=Never)


@dataclasses.dataclass(frozen=True)
class AwaitableResultWrapper(BaseAwaitableWrapper[Result[_F_co, _S_co]]):
    @staticmethod
    def construct_failure(value: _F) -> AwaitableResultWrapper[_F, Never]:
        return AwaitableResultWrapper(awaitable_result.construct_failure(value))

    @staticmethod
    def construct_failure_from_awaitable(
        awtbl: Awaitable[_F],
    ) -> AwaitableResultWrapper[_F, Never]:
        return AwaitableResultWrapper(
            awaitable_result.construct_failure_from_awaitable(awtbl)
        )

    @staticmethod
    def construct_from_awaitable_result(
        a_rslt: AwaitableResult[_F, _S],
    ) -> AwaitableResultWrapper[_F, _S]:
        return AwaitableResultWrapper(a_rslt)

    @staticmethod
    def construct_from_result(rslt: Result[_F, _S]) -> AwaitableResultWrapper[_F, _S]:
        return AwaitableResultWrapper(awaitable_result.construct_from_result(rslt))

    @staticmethod
    def construct_success(value: _S) -> AwaitableResultWrapper[Never, _S]:
        return AwaitableResultWrapper(awaitable_result.construct_success(value))

    @staticmethod
    def construct_success_from_awaitable(
        awtbl: Awaitable[_S],
    ) -> AwaitableResultWrapper[Never, _S]:
        return AwaitableResultWrapper(
            awaitable_result.construct_success_from_awaitable(awtbl)
        )

    def map_failure(
        self, f: Callable[[_F_co], _F]
    ) -> AwaitableResultWrapper[_F, _S_co]:
        f_mapped = awaitable_result.map_failure(f)
        return AwaitableResultWrapper(f_mapped(self.core))

    def map_failure_to_awaitable(
        self, f: Callable[[_F_co], Awaitable[_F]]
    ) -> AwaitableResultWrapper[_F, _S_co]:
        f_mapped = awaitable_result.map_failure_to_awaitable(f)
        return AwaitableResultWrapper(f_mapped(self.core))

    def map_failure_to_awaitable_result(
        self, f: Callable[[_F_co], AwaitableResult[_F, _S]]
    ) -> AwaitableResultWrapper[_F, _S_co | _S]:
        f_mapped = awaitable_result.map_failure_to_awaitable_result(f)
        return AwaitableResultWrapper(f_mapped(self.core))

    def map_failure_to_result(
        self, f: Callable[[_F_co], Result[_F, _S]]
    ) -> AwaitableResultWrapper[_F, _S_co | _S]:
        f_mapped = awaitable_result.map_failure_to_result(f)
        return AwaitableResultWrapper(f_mapped(self.core))

    def map_success(
        self, f: Callable[[_S_co], _S]
    ) -> AwaitableResultWrapper[_F_co, _S]:
        f_mapped = awaitable_result.map_success(f)
        return AwaitableResultWrapper(f_mapped(self.core))

    def map_success_to_awaitable(
        self, f: Callable[[_S_co], Awaitable[_S]]
    ) -> AwaitableResultWrapper[_F_co, _S]:
        f_mapped = awaitable_result.map_success_to_awaitable(f)
        return AwaitableResultWrapper(f_mapped(self.core))

    def map_success_to_awaitable_result(
        self, f: Callable[[_S_co], AwaitableResult[_F, _S]]
    ) -> AwaitableResultWrapper[_F_co | _F, _S]:
        f_mapped = awaitable_result.map_success_to_awaitable_result(f)
        return AwaitableResultWrapper(f_mapped(self.core))

    def map_success_to_result(
        self, f: Callable[[_S_co], Result[_F, _S]]
    ) -> AwaitableResultWrapper[_F_co | _F, _S]:
        f_mapped = awaitable_result.map_success_to_result(f)
        return AwaitableResultWrapper(f_mapped(self.core))

    @property
    async def track(self) -> Literal["failure", "success"]:
        return (await self.core)[0]

    @property
    async def value(self) -> _F_co | _S_co:
        return (await self.core)[1]


__docformat__ = "google"
