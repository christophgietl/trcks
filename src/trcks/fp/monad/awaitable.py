from __future__ import annotations

from typing import TYPE_CHECKING

from trcks._typing_extensions import TypeVar

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

_T = TypeVar("_T")
_T1 = TypeVar("_T1")
_T2 = TypeVar("_T2")


async def construct(value: _T) -> _T:
    return value


def map_(f: Callable[[_T1], _T2]) -> Callable[[Awaitable[_T1]], Awaitable[_T2]]:
    async def f_mapped(awaitable: Awaitable[_T1]) -> _T2:
        return f(await awaitable)

    return f_mapped


def map_to_awaitable(
    f: Callable[[_T1], Awaitable[_T2]],
) -> Callable[[Awaitable[_T1]], Awaitable[_T2]]:
    async def f_mapped(awaitable: Awaitable[_T1]) -> _T2:
        return await f(await awaitable)

    return f_mapped
