from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING, Generic, TypeVar

if TYPE_CHECKING:
    from collections.abc import Callable

_T = TypeVar("_T")

_Core_co = TypeVar("_Core_co", covariant=True)


@dataclasses.dataclass(frozen=True)
class TrackHelper(Generic[_Core_co]):
    core: _Core_co

    @staticmethod
    def unwrap_return_value(
        f: Callable[[_T], TrackHelper[_Core_co]],
    ) -> Callable[[_T], _Core_co]:
        def f_unwrapped(value: _T) -> _Core_co:
            return f(value).core

        return f_unwrapped
