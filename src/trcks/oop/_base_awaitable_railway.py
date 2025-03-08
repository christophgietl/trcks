from __future__ import annotations

import dataclasses
from collections.abc import Awaitable

from trcks._typing import TypeVar
from trcks.oop._base_railway import BaseRailway

_T_co = TypeVar("_T_co", covariant=True)


@dataclasses.dataclass(frozen=True)
class BaseAwaitableRailway(BaseRailway[Awaitable[_T_co]]):
    @property
    async def freight_as_coroutine(self) -> _T_co:
        return await self.freight


__docformat__ = "google"
