from collections.abc import Awaitable

from trcks._typing import TypeVar
from trcks.oop._abstract_wrapper import AbstractWrapper

__docformat__ = "google"

_T_co = TypeVar("_T_co", covariant=True)


class AbstractAwaitableWrapper(AbstractWrapper[Awaitable[_T_co]]):
    """Abstract base class for all asynchronous wrappers in
    the [trcks.oop][] package.

    Note:
        This class is abstract and cannot be instantiated directly.
        If you want to wrap an [collections.abc.Awaitable][],
        please use one of the concrete subclasses instead,
        such as [trcks.oop.AwaitableWrapper][].

    Example:
        >>> import asyncio
        >>> from trcks.oop import AbstractAwaitableWrapper
        >>> awtbl = asyncio.sleep(0.001)
        >>> AbstractAwaitableWrapper(awtbl)
        Traceback (most recent call last):
            ...
        TypeError: Can't instantiate abstract class AbstractAwaitableWrapper ...
        >>> asyncio.run(awtbl)
    """

    __slots__: tuple[str, ...] = ()

    @property
    async def core_as_coroutine(self) -> _T_co:
        """The wrapped [collections.abc.Awaitable][] object
        transformed into a coroutine.

        This is useful for functions that expect a coroutine (e.g. [asyncio.run][]).

        Note:
            The attribute [trcks.oop.AbstractAwaitableWrapper.core][]
            has type [collections.abc.Awaitable][],
            a superclass of [collections.abc.Coroutine][].
        """
        return await self.core
