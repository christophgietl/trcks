from collections.abc import Awaitable

from trcks._typing import TypeVar
from trcks.oop._base_wrapper import BaseWrapper

__docformat__ = "google"

_T_co = TypeVar("_T_co", covariant=True)


class BaseAwaitableWrapper(BaseWrapper[Awaitable[_T_co]]):
    """Base class for all asynchronous wrappers in the [trcks.oop][] package.

    Note:
        This class is not particularly useful by itself.
        If you want to wrap and process a value,
        please consider using one of its subclasses,
        such as [trcks.oop.AwaitableWrapper][].
    """

    __slots__: tuple[str, ...] = ()

    @property
    async def core_as_coroutine(self) -> _T_co:
        """The wrapped [collections.abc.Awaitable][] object
        transformed into a coroutine.

        This is useful for functions that expect a coroutine (e.g. [asyncio.run][]).

        Note:
            The attribute [trcks.oop.BaseWrapper.core][]
            has type [collections.abc.Awaitable][],
            a superclass of [collections.abc.Coroutine][].

        Example:
            >>> import asyncio
            >>> from trcks.oop import BaseAwaitableWrapper
            >>> loop = asyncio.new_event_loop()
            >>> asyncio.set_event_loop(loop)
            >>> future = asyncio.Future[str]()
            >>> future.set_result("Hello, world!")
            >>> wrapped_future = BaseAwaitableWrapper(future)
            >>> wrapped_future
            BaseAwaitableWrapper(core=<Future finished result='Hello, world!'>)
            >>> coro = wrapped_future.core_as_coroutine
            >>> coro
            <coroutine object BaseAwaitableWrapper.core_as_coroutine at 0x...>
            >>> asyncio.run(coro)
            'Hello, world!'
            >>> loop.close()
        """
        return await self.core
