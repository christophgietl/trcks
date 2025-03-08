from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING

from trcks._typing import TypeVar
from trcks.fp.monads import awaitable
from trcks.oop._awaitable_result_railway import AwaitableResultRailway
from trcks.oop._base_awaitable_railway import BaseAwaitableRailway

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Awaitable, Callable

    from trcks import AwaitableResult, Result


_F = TypeVar("_F")
_S = TypeVar("_S")
_T = TypeVar("_T")

_T_co = TypeVar("_T_co", covariant=True)


@dataclasses.dataclass(frozen=True)
class AwaitableRailway(BaseAwaitableRailway[_T_co]):
    @staticmethod
    def construct(value: _T) -> AwaitableRailway[_T]:
        return AwaitableRailway(awaitable.construct(value))

    @staticmethod
    def construct_from_awaitable(awtbl: Awaitable[_T]) -> AwaitableRailway[_T]:
        return AwaitableRailway(awtbl)

    def map(self, f: Callable[[_T_co], _T]) -> AwaitableRailway[_T]:
        f_mapped = awaitable.map_(f)
        return AwaitableRailway(f_mapped(self.core))

    def map_to_awaitable(
        self, f: Callable[[_T_co], Awaitable[_T]]
    ) -> AwaitableRailway[_T]:
        f_mapped = awaitable.map_to_awaitable(f)
        return AwaitableRailway(f_mapped(self.core))

    def map_to_awaitable_result(
        self, f: Callable[[_T_co], AwaitableResult[_F, _S]]
    ) -> AwaitableResultRailway[_F, _S]:
        return AwaitableResultRailway.construct_success_from_awaitable(
            self.core
        ).map_success_to_awaitable_result(f)

    def map_to_result(
        self, f: Callable[[_T_co], Result[_F, _S]]
    ) -> AwaitableResultRailway[_F, _S]:
        return AwaitableResultRailway.construct_success_from_awaitable(
            self.core
        ).map_success_to_result(f)


__docformat__ = "google"
