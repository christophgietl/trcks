from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING

from trcks._typing import TypeVar
from trcks.oop._awaitable_result_wrapper import AwaitableResultWrapper
from trcks.oop._awaitable_wrapper import AwaitableWrapper
from trcks.oop._base_wrapper import BaseWrapper
from trcks.oop._result_wrapper import ResultWrapper

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Awaitable, Callable

    from trcks import AwaitableResult, Result

_F = TypeVar("_F")
_S = TypeVar("_S")
_T = TypeVar("_T")

_T_co = TypeVar("_T_co", covariant=True)


@dataclasses.dataclass(frozen=True)
class Wrapper(BaseWrapper[_T_co]):
    @staticmethod
    def construct(value: _T) -> Wrapper[_T]:
        return Wrapper(value)

    def map(self, f: Callable[[_T_co], _T]) -> Wrapper[_T]:
        return Wrapper(f(self.core))

    def map_to_awaitable(
        self, f: Callable[[_T_co], Awaitable[_T]]
    ) -> AwaitableWrapper[_T]:
        return AwaitableWrapper(f(self.core))

    def map_to_awaitable_result(
        self, f: Callable[[_T_co], AwaitableResult[_F, _S]]
    ) -> AwaitableResultWrapper[_F, _S]:
        return AwaitableResultWrapper(f(self.core))

    def map_to_result(
        self, f: Callable[[_T_co], Result[_F, _S]]
    ) -> ResultWrapper[_F, _S]:
        return ResultWrapper(f(self.core))


__docformat__ = "google"
