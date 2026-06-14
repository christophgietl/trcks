from __future__ import annotations

from typing import TYPE_CHECKING

from trcks._typing import TypeVar, deprecated
from trcks.fp.monads import awaitable_tuple as at
from trcks.oop._base_awaitable_wrapper import BaseAwaitableWrapper

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable, Iterable

    from trcks import (
        AwaitableIterable,
        AwaitableTuple,
    )

__docformat__ = "google"

_T = TypeVar("_T")

_T_co = TypeVar("_T_co", covariant=True)


class AwaitableTupleWrapper(BaseAwaitableWrapper[tuple[_T_co, ...]]):
    """Type-safe and immutable wrapper for [trcks.AwaitableTuple][] objects.

    The wrapped object can be accessed
    via the attribute [trcks.oop.BaseWrapper.core][].
    The `trcks.oop.AwaitableTupleWrapper.map*` methods allow method chaining.
    The `trcks.oop.AwaitableTupleWrapper.tap*` methods allow for side effects
    without changing the wrapped tuple.

    Example:
        >>> import asyncio
        >>> from trcks.oop import AwaitableTupleWrapper
        >>> async def slowly_double(n: int) -> int:
        ...     await asyncio.sleep(0.001)
        ...     return n * 2
        ...
        >>> async def main() -> tuple[int, ...]:
        ...     return await (
        ...         AwaitableTupleWrapper
        ...         .construct_from_iterable((1, 2, 3))
        ...         .map_to_awaitable(slowly_double)
        ...         .core
        ...     )
        ...
        >>> asyncio.run(main())
        (2, 4, 6)
    """

    __slots__: tuple[str, ...] = ()

    @staticmethod
    def construct(value: _T) -> AwaitableTupleWrapper[_T]:
        """Construct and wrap a [trcks.AwaitableTuple][] object from a value.

        Args:
            value: The value to be wrapped.

        Returns:
            A new [trcks.oop.AwaitableTupleWrapper][] instance with
                the wrapped [trcks.AwaitableTuple][] object.

        Example:
            >>> import asyncio
            >>> from trcks.oop import AwaitableTupleWrapper
            >>> awaitable_tuple_wrapper = AwaitableTupleWrapper.construct(42)
            >>> awaitable_tuple_wrapper
            AwaitableTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_tuple_wrapper.core_as_coroutine)
            (42,)
        """
        return AwaitableTupleWrapper(at.construct(value))

    @staticmethod
    def construct_from_awaitable(
        awtbl: Awaitable[_T],
    ) -> AwaitableTupleWrapper[_T]:
        """Construct and wrap a [trcks.AwaitableTuple][] from an awaitable value.

        Args:
            awtbl: The awaitable value to be wrapped.

        Returns:
            A new [trcks.oop.AwaitableTupleWrapper][] instance with
                the wrapped [trcks.AwaitableTuple][] object.

        Example:
            >>> import asyncio
            >>> from trcks.oop import AwaitableTupleWrapper
            >>> async def slowly_get_value() -> int:
            ...     await asyncio.sleep(0.001)
            ...     return 7
            ...
            >>> awaitable_tuple_wrapper = (
            ...     AwaitableTupleWrapper
            ...     .construct_from_awaitable(slowly_get_value())
            ... )
            >>> awaitable_tuple_wrapper
            AwaitableTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_tuple_wrapper.core_as_coroutine)
            (7,)
        """
        return AwaitableTupleWrapper(at.construct_from_awaitable(awtbl))

    @staticmethod
    def construct_from_iterable(it: Iterable[_T]) -> AwaitableTupleWrapper[_T]:
        """Construct and wrap a [trcks.AwaitableTuple][] from an iterable.

        Args:
            it: The [collections.abc.Iterable][] to be wrapped and converted.

        Returns:
            A new [trcks.oop.AwaitableTupleWrapper][] instance with
                the wrapped [trcks.AwaitableTuple][] object.

        Example:
            >>> import asyncio
            >>> from trcks.oop import AwaitableTupleWrapper
            >>> awaitable_tuple_wrapper = (
            ...     AwaitableTupleWrapper
            ...     .construct_from_iterable([1, 2])
            ... )
            >>> awaitable_tuple_wrapper
            AwaitableTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_tuple_wrapper.core_as_coroutine)
            (1, 2)
        """
        return AwaitableTupleWrapper(at.construct_from_iterable(it))

    @classmethod
    @deprecated("Use construct_from_iterable or the default constructor instead")
    def construct_from_tuple(
        cls,
        tpl: tuple[_T, ...],
    ) -> AwaitableTupleWrapper[_T]:
        """Deprecated alias for construct_from_iterable."""
        return cls.construct_from_iterable(tpl)  # pragma: no cover

    def map(self, f: Callable[[_T_co], _T]) -> AwaitableTupleWrapper[_T]:
        """Apply a synchronous function to each element in the wrapped
        [trcks.AwaitableTuple][] object.

        Args:
            f: The synchronous function to be applied to each element.

        Returns:
            A new [trcks.oop.AwaitableTupleWrapper][] instance with
                the wrapped [trcks.AwaitableTuple][] object containing
                the results of applying the function to each element.

        Example:
            >>> import asyncio
            >>> from trcks.oop import AwaitableTupleWrapper
            >>> def double_integer(n: int) -> int:
            ...     return n * 2
            ...
            >>> awaitable_tuple_wrapper: AwaitableTupleWrapper[int] = (
            ...     AwaitableTupleWrapper
            ...     .construct_from_iterable((1, 2, 3))
            ...     .map(double_integer)
            ... )
            >>> awaitable_tuple_wrapper
            AwaitableTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_tuple_wrapper.core_as_coroutine)
            (2, 4, 6)
        """
        return AwaitableTupleWrapper(at.map_(f)(self.core))

    def map_to_awaitable(
        self, f: Callable[[_T_co], Awaitable[_T]]
    ) -> AwaitableTupleWrapper[_T]:
        """Apply an asynchronous function to each element in the wrapped
        [trcks.AwaitableTuple][] object.

        Args:
            f: The asynchronous function to be applied to each element.

        Returns:
            A new [trcks.oop.AwaitableTupleWrapper][] instance with
                the wrapped [trcks.AwaitableTuple][] object containing
                the results of applying the function to each element.

        Example:
            >>> import asyncio
            >>> from trcks.oop import AwaitableTupleWrapper
            >>> async def slowly_add_one(n: int) -> int:
            ...     await asyncio.sleep(0.001)
            ...     return n + 1
            ...
            >>> awaitable_tuple_wrapper: AwaitableTupleWrapper[int] = (
            ...     AwaitableTupleWrapper
            ...     .construct_from_iterable((1, 2))
            ...     .map_to_awaitable(slowly_add_one)
            ... )
            >>> awaitable_tuple_wrapper
            AwaitableTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_tuple_wrapper.core_as_coroutine)
            (2, 3)
        """
        return AwaitableTupleWrapper(at.map_to_awaitable(f)(self.core))

    def map_to_awaitable_iterable(
        self, f: Callable[[_T_co], AwaitableIterable[_T]]
    ) -> AwaitableTupleWrapper[_T]:
        """Apply an asynchronous function returning a [trcks.AwaitableIterable][]
        to each element in the wrapped [trcks.AwaitableTuple][] and flatten.

        Args:
            f: The asynchronous function to be applied to each element,
                returning a [trcks.AwaitableIterable][].

        Returns:
            A new [trcks.oop.AwaitableTupleWrapper][] instance with
                the flattened [trcks.AwaitableTuple][] object.

        Example:
            >>> import asyncio
            >>> from trcks.oop import AwaitableTupleWrapper
            >>> async def slowly_duplicate(n: int) -> tuple[int, int]:
            ...     await asyncio.sleep(0.001)
            ...     return n, n
            ...
            >>> awaitable_tuple_wrapper: AwaitableTupleWrapper[int] = (
            ...     AwaitableTupleWrapper
            ...     .construct_from_iterable((1, 2))
            ...     .map_to_awaitable_iterable(slowly_duplicate)
            ... )
            >>> awaitable_tuple_wrapper
            AwaitableTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_tuple_wrapper.core_as_coroutine)
            (1, 1, 2, 2)
        """
        return AwaitableTupleWrapper(at.map_to_awaitable_iterable(f)(self.core))

    @deprecated("Use map_to_awaitable_iterable instead")
    def map_to_awaitable_tuple(
        self, f: Callable[[_T_co], AwaitableTuple[_T]]
    ) -> AwaitableTupleWrapper[_T]:
        """Deprecated alias for
        [trcks.oop.AwaitableTupleWrapper.map_to_awaitable_iterable][].
        """
        return self.map_to_awaitable_iterable(f)  # pragma: no cover

    def map_to_iterable(
        self, f: Callable[[_T_co], Iterable[_T]]
    ) -> AwaitableTupleWrapper[_T]:
        """Apply a synchronous function returning an [collections.abc.Iterable][]
        to each element in the wrapped [trcks.AwaitableTuple][] object and flatten.

        Args:
            f: The synchronous function to be applied to each element,
                returning an [collections.abc.Iterable][].

        Returns:
            A new [trcks.oop.AwaitableTupleWrapper][] instance with
                the flattened [trcks.AwaitableTuple][] object.

        Example:
            >>> import asyncio
            >>> from trcks.oop import AwaitableTupleWrapper
            >>> def add_negative(n: int) -> tuple[int, int]:
            ...     return n, -n
            ...
            >>> awaitable_tuple_wrapper: AwaitableTupleWrapper[int] = (
            ...     AwaitableTupleWrapper
            ...     .construct_from_iterable((1, 2))
            ...     .map_to_iterable(add_negative)
            ... )
            >>> awaitable_tuple_wrapper
            AwaitableTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_tuple_wrapper.core_as_coroutine)
            (1, -1, 2, -2)
        """
        return AwaitableTupleWrapper(at.map_to_iterable(f)(self.core))

    @deprecated("Use map_to_iterable instead")
    def map_to_tuple(
        self, f: Callable[[_T_co], tuple[_T, ...]]
    ) -> AwaitableTupleWrapper[_T]:
        """Deprecated alias for
        [trcks.oop.AwaitableTupleWrapper.map_to_iterable][].
        """
        return self.map_to_iterable(f)  # pragma: no cover

    def tap(self, f: Callable[[_T_co], object]) -> AwaitableTupleWrapper[_T_co]:
        """Apply a synchronous side effect to each element in the wrapped
        [trcks.AwaitableTuple][] object.

        Args:
            f: The synchronous side effect to be applied to each element.

        Returns:
            A new [trcks.oop.AwaitableTupleWrapper][] instance with
                the original [trcks.AwaitableTuple][] object.

        Example:
            >>> import asyncio
            >>> from trcks.oop import AwaitableTupleWrapper
            >>> def log_integer(n: int) -> None:
            ...     print(f"Received: {n}")
            ...
            >>> awaitable_tuple_wrapper: AwaitableTupleWrapper[int] = (
            ...     AwaitableTupleWrapper
            ...     .construct_from_iterable((1, 2))
            ...     .tap(log_integer)
            ... )
            >>> awaitable_tuple_wrapper
            AwaitableTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_tuple_wrapper.core_as_coroutine)
            Received: 1
            Received: 2
            (1, 2)
        """
        return AwaitableTupleWrapper(at.tap(f)(self.core))

    def tap_to_awaitable(
        self, f: Callable[[_T_co], Awaitable[object]]
    ) -> AwaitableTupleWrapper[_T_co]:
        """Apply an asynchronous side effect to each element in the wrapped
        [trcks.AwaitableTuple][] object.

        Args:
            f: The asynchronous side effect to be applied to each element.

        Returns:
            A new [trcks.oop.AwaitableTupleWrapper][] instance with
                the original [trcks.AwaitableTuple][] object.

        Example:
            >>> import asyncio
            >>> from trcks.oop import AwaitableTupleWrapper
            >>> async def slowly_log(n: int) -> None:
            ...     await asyncio.sleep(0.001)
            ...     print(f"Logged: {n}")
            ...
            >>> awaitable_tuple_wrapper: AwaitableTupleWrapper[int] = (
            ...     AwaitableTupleWrapper
            ...     .construct_from_iterable((1, 2))
            ...     .tap_to_awaitable(slowly_log)
            ... )
            >>> awaitable_tuple_wrapper
            AwaitableTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_tuple_wrapper.core_as_coroutine)
            Logged: 1
            Logged: 2
            (1, 2)
        """
        return AwaitableTupleWrapper(at.tap_to_awaitable(f)(self.core))

    def tap_to_awaitable_iterable(
        self, f: Callable[[_T_co], AwaitableIterable[object]]
    ) -> AwaitableTupleWrapper[_T_co]:
        """Apply an asynchronous side effect returning a [trcks.AwaitableIterable][]
        to each element in the wrapped [trcks.AwaitableTuple][] object.

        Args:
            f: The asynchronous side effect to be applied to each element,
                returning a [trcks.AwaitableIterable][].

        Returns:
            A new [trcks.oop.AwaitableTupleWrapper][] instance with
                the original [trcks.AwaitableTuple][] object.

        Example:
            >>> import asyncio
            >>> from trcks.oop import AwaitableTupleWrapper
            >>> async def slowly_get_divisors(n: int) -> tuple[int, ...]:
            ...     await asyncio.sleep(0.001)
            ...     candidates = range(1, n + 1)
            ...     return tuple(c for c in candidates if n % c == 0)
            ...
            >>> awaitable_tuple_wrapper: AwaitableTupleWrapper[int] = (
            ...     AwaitableTupleWrapper
            ...     .construct_from_iterable((1, 2, 3, 4))
            ...     .tap_to_awaitable_iterable(slowly_get_divisors)
            ... )
            >>> awaitable_tuple_wrapper
            AwaitableTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_tuple_wrapper.core_as_coroutine)
            (1, 2, 2, 3, 3, 4, 4, 4)
        """
        return AwaitableTupleWrapper(at.tap_to_awaitable_iterable(f)(self.core))

    @deprecated("Use tap_to_awaitable_iterable instead")
    def tap_to_awaitable_tuple(
        self, f: Callable[[_T_co], AwaitableTuple[object]]
    ) -> AwaitableTupleWrapper[_T_co]:
        """Deprecated alias for
        [trcks.oop.AwaitableTupleWrapper.tap_to_awaitable_iterable][].
        """
        return self.tap_to_awaitable_iterable(f)  # pragma: no cover

    def tap_to_iterable(
        self, f: Callable[[_T_co], Iterable[object]]
    ) -> AwaitableTupleWrapper[_T_co]:
        """Apply a synchronous side effect returning an [collections.abc.Iterable][]
        to each element in the wrapped [trcks.AwaitableTuple][] object.

        Args:
            f: The synchronous side effect to be applied to each element,
                returning an [collections.abc.Iterable][].

        Returns:
            A new [trcks.oop.AwaitableTupleWrapper][] instance with
                the original [trcks.AwaitableTuple][] object.

        Example:
            >>> import asyncio
            >>> from trcks.oop import AwaitableTupleWrapper
            >>> def get_divisors(n: int) -> tuple[int, ...]:
            ...     candidates = range(1, n + 1)
            ...     return tuple(c for c in candidates if n % c == 0)
            ...
            >>> awaitable_tuple_wrapper: AwaitableTupleWrapper[int] = (
            ...     AwaitableTupleWrapper
            ...     .construct_from_iterable((1, 2, 3, 4))
            ...     .tap_to_iterable(get_divisors)
            ... )
            >>> awaitable_tuple_wrapper
            AwaitableTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_tuple_wrapper.core_as_coroutine)
            (1, 2, 2, 3, 3, 4, 4, 4)
        """
        return AwaitableTupleWrapper(at.tap_to_iterable(f)(self.core))

    @deprecated("Use tap_to_iterable instead")
    def tap_to_tuple(
        self, f: Callable[[_T_co], tuple[object, ...]]
    ) -> AwaitableTupleWrapper[_T_co]:
        """Deprecated alias for
        [trcks.oop.AwaitableTupleWrapper.tap_to_iterable][].
        """
        return self.tap_to_iterable(f)  # pragma: no cover
