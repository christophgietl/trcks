from collections.abc import Awaitable

from trcks._typing import TypeVar
from trcks.oop._base_wrapper import BaseWrapper

__docformat__ = "google"

_T_co = TypeVar("_T_co", covariant=True)


class BaseAwaitableWrapper(BaseWrapper[Awaitable[_T_co]]):
    """Base class for all asynchronous wrappers in the [trcks.oop][] package."""

    __slots__: tuple[str, ...] = ()

    @property
    async def core_as_coroutine(self) -> _T_co:
        """The wrapped [collections.abc.Awaitable][] object
        transformed into a coroutine.

        This is useful for functions that expect a coroutine (e.g. [asyncio.run][]).

        Note:
            The attribute
            [trcks.oop._base_awaitable_wrapper.BaseAwaitableWrapper.core][]
            has type [collections.abc.Awaitable][],
            a superclass of [collections.abc.Coroutine][].
        """
        return await self.core
