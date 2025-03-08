from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING

from trcks._typing import TypeVar
from trcks.oop._awaitable_railway import AwaitableRailway
from trcks.oop._awaitable_result_railway import AwaitableResultRailway
from trcks.oop._base_railway import BaseRailway
from trcks.oop._result_railway import ResultRailway

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Awaitable, Callable

    from trcks import AwaitableResult, Result

_F = TypeVar("_F")
_S = TypeVar("_S")
_T = TypeVar("_T")

_T_co = TypeVar("_T_co", covariant=True)


@dataclasses.dataclass(frozen=True)
class Railway(BaseRailway[_T_co]):
    @staticmethod
    def construct(value: _T) -> Railway[_T]:
        return Railway(value)

    def map(self, f: Callable[[_T_co], _T]) -> Railway[_T]:
        return Railway(f(self.freight))

    def map_to_awaitable(
        self, f: Callable[[_T_co], Awaitable[_T]]
    ) -> AwaitableRailway[_T]:
        return AwaitableRailway(f(self.freight))

    def map_to_awaitable_result(
        self, f: Callable[[_T_co], AwaitableResult[_F, _S]]
    ) -> AwaitableResultRailway[_F, _S]:
        return AwaitableResultRailway(f(self.freight))

    def map_to_result(
        self, f: Callable[[_T_co], Result[_F, _S]]
    ) -> ResultRailway[_F, _S]:
        return ResultRailway(f(self.freight))


__docformat__ = "google"
