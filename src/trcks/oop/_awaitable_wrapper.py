from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING

from trcks._typing import TypeVar
from trcks.fp.monads import awaitable as a
from trcks.oop._awaitable_result_wrapper import AwaitableResultWrapper
from trcks.oop._base_awaitable_wrapper import BaseAwaitableWrapper

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Awaitable, Callable

    from trcks import AwaitableResult, Result

__docformat__ = "google"

_F = TypeVar("_F")
_S = TypeVar("_S")
_T = TypeVar("_T")

_T_co = TypeVar("_T_co", covariant=True)


@dataclasses.dataclass(frozen=True)
class AwaitableWrapper(BaseAwaitableWrapper[_T_co]):
    """Typesafe and immutable wrapper for `collections.abc.Awaitable` objects.

    The wrapped `collections.abc.Awaitable` can be accessed
    via the attribute `AwaitableWrapper.core`.
    The ``AwaitableWrapper.map*`` methods allow method chaining.

    Example:
        >>> import asyncio
        >>> from trcks.oop import AwaitableWrapper
        >>> async def read_from_disk() -> str:
        ...     await asyncio.sleep(0.001)
        ...     input_ = "Hello, world!"
        ...     print(f"Read '{input_}' from disk.")
        ...     return input_
        ...
        >>> def transform(s: str) -> str:
        ...     return f"Length: {len(s)}"
        ...
        >>> async def write_to_disk(output: str) -> None:
        ...     await asyncio.sleep(0.001)
        ...     print(f"Wrote '{output}' to disk.")
        ...
        >>> async def main() -> None:
        ...     awaitable_str = read_from_disk()
        ...     return await (
        ...         AwaitableWrapper
        ...         .construct_from_awaitable(awaitable_str)
        ...         .map(transform)
        ...         .map_to_awaitable(write_to_disk)
        ...         .core
        ...     )
        ...
        >>> asyncio.run(main())
        Read 'Hello, world!' from disk.
        Wrote 'Length: 13' to disk.
    """

    @staticmethod
    def construct(value: _T) -> AwaitableWrapper[_T]:
        """Construct and wrap an `collections.abc.Awaitable` object from a value.

        Args:
            value: The value to be wrapped.

        Returns:
            A new `AwaitableWrapper` instance
            with the wrapped `collections.abc.Awaitable` object.

        Example:
            >>> import asyncio
            >>> from trcks.oop import AwaitableWrapper
            >>> awaitable_wrapper = AwaitableWrapper.construct("Hello, world!")
            >>> awaitable_wrapper
            AwaitableWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_wrapper.core_as_coroutine)
            'Hello, world!'
        """
        return AwaitableWrapper(a.construct(value))

    @staticmethod
    def construct_from_awaitable(awtbl: Awaitable[_T]) -> AwaitableWrapper[_T]:
        """Alias for the default constructor.

        Args:
            awtbl: The `collections.abc.Awaitable` to be wrapped.

        Returns:
            A new `AwaitableWrapper` instance
            with the wrapped `collections.abc.Awaitable` object.

        Example:
            >>> import asyncio
            >>> from trcks.oop import AwaitableWrapper
            >>> async def read_from_disk() -> str:
            ...     return await asyncio.sleep(0.001, result="Hello, world!")
            ...
            >>> awaitable_str = read_from_disk()
            >>> awaitable_wrapper = AwaitableWrapper.construct_from_awaitable(
            ...     awaitable_str
            ... )
            >>> awaitable_wrapper
            AwaitableWrapper(core=<coroutine object read_from_disk at 0x...>)
            >>> asyncio.run(awaitable_wrapper.core_as_coroutine)
            'Hello, world!'
        """
        return AwaitableWrapper(awtbl)

    def map(self, f: Callable[[_T_co], _T]) -> AwaitableWrapper[_T]:
        """Apply a sync. function to the wrapped `collections.abc.Awaitable` object.

        Args:
            f: The synchronous function to be applied.

        Returns:
            A new `AwaitableWrapper` instance with
            the result of the function application.

        Example:
            >>> import asyncio
            >>> from trcks.oop import AwaitableWrapper
            >>> def transform(s: str) -> str:
            ...     return f"Length: {len(s)}"
            ...
            >>> awaitable_wrapper = (
            ...     AwaitableWrapper
            ...     .construct("Hello, world!")
            ...     .map(transform)
            ... )
            >>> awaitable_wrapper
            AwaitableWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_wrapper.core_as_coroutine)
            'Length: 13'
        """
        mapped_f = a.map_(f)
        return AwaitableWrapper(mapped_f(self.core))

    def map_to_awaitable(
        self, f: Callable[[_T_co], Awaitable[_T]]
    ) -> AwaitableWrapper[_T]:
        """Apply an async. function to the wrapped `collections.abc.Awaitable` object.

        Args:
            f: The asynchronous function to be applied.

        Returns:
            A new `AwaitableWrapper` instance with
            the result of the function application.

        Example:
            >>> import asyncio
            >>> from trcks.oop import AwaitableWrapper
            >>> async def write_to_disk(output: str) -> None:
            ...     await asyncio.sleep(0.001)
            ...     print(f"Wrote '{output}' to disk.")
            ...
            >>> awaitable_wrapper = (
            ...     AwaitableWrapper
            ...     .construct("Hello, world!")
            ...     .map_to_awaitable(write_to_disk)
            ... )
            >>> awaitable_wrapper
            AwaitableWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_wrapper.core_as_coroutine)
            Wrote 'Hello, world!' to disk.
        """
        mapped_f = a.map_to_awaitable(f)
        return AwaitableWrapper(mapped_f(self.core))

    def map_to_awaitable_result(
        self, f: Callable[[_T_co], AwaitableResult[_F, _S]]
    ) -> AwaitableResultWrapper[_F, _S]:
        """Apply an asynchronous function with return type `trcks.Result`.

        Args:
            f: The asynchronous function to be applied.

        Returns:
            An `AwaitableResultWrapper` instance with
            the result of the function application.

        Example:
            >>> import asyncio
            >>> from trcks import Result
            >>> from trcks.oop import AwaitableWrapper
            >>> async def slowly_assert_non_negative(
            ...     x: float,
            ... ) -> Result[str, float]:
            ...     await asyncio.sleep(0.001)
            ...     if x < 0:
            ...         return ("failure", "negative value")
            ...     return ("success", x)
            ...
            >>> awaitable_result_wrapper = (
            ...     AwaitableWrapper
            ...     .construct(42.0)
            ...     .map_to_awaitable_result(slowly_assert_non_negative)
            ... )
            >>> awaitable_result_wrapper
            AwaitableResultWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_result_wrapper.core_as_coroutine)
            ('success', 42.0)
        """
        return AwaitableResultWrapper.construct_success_from_awaitable(
            self.core
        ).map_success_to_awaitable_result(f)

    def map_to_result(
        self, f: Callable[[_T_co], Result[_F, _S]]
    ) -> AwaitableResultWrapper[_F, _S]:
        """Apply a sync. function with return type `trcks.Result`.

        Args:
            f: The synchronous function to be applied.

        Returns:
            An `AwaitableResultWrapper` instance with
            the result of the function application.

        Example:
            >>> import asyncio
            >>> from trcks.oop import AwaitableWrapper
            >>> awaitable_result_wrapper = (
            ...     AwaitableWrapper
            ...     .construct(-1)
            ...     .map_to_result(
            ...         lambda x: ("success", x)
            ...         if x >= 0
            ...         else ("failure", "negative value")
            ...     )
            ... )
            >>> awaitable_result_wrapper
            AwaitableResultWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_result_wrapper.core_as_coroutine)
            ('failure', 'negative value')
        """
        return AwaitableResultWrapper.construct_success_from_awaitable(
            self.core
        ).map_success_to_result(f)
