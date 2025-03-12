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

__docformat__ = "google"

_F = TypeVar("_F")
_S = TypeVar("_S")
_T = TypeVar("_T")

_T_co = TypeVar("_T_co", covariant=True)


@dataclasses.dataclass(frozen=True)
class Wrapper(BaseWrapper[_T_co]):
    """Typesafe and immutable wrapper for arbitrary objects.

    The wrapped object can be accessed via the attribute `Wrapper.core`.
    The ``Wrapper.map*`` methods allow method chaining.

    Example:
        The string ``"Hello"`` is wrapped and manipulated in the following example.
        Finally, the result is unwrapped:

            >>> wrapper = (
            ...     Wrapper(core="Hello").map(len).map(lambda n: f"Length: {n}")
            ... )
            >>> wrapper
            Wrapper(core='Length: 5')
            >>> wrapper.core
            'Length: 5'
    """

    @staticmethod
    def construct(value: _T) -> Wrapper[_T]:
        """Alias for the default constructor.

        Args:
            value: The object to be wrapped.

        Returns:
            A new `Wrapper` instance with the wrapped object.

        Example:
            >>> Wrapper.construct(5)
            Wrapper(core=5)
        """
        return Wrapper(core=value)

    def map(self, f: Callable[[_T_co], _T]) -> Wrapper[_T]:
        """Apply a synchronous function to the wrapped object.

        Args:
            f: The synchronous function to be applied.

        Returns:
            A new `Wrapper` instance with the result of the function application.

        Example:
            >>> Wrapper.construct(5).map(lambda n: f"The number is {n}.")
            Wrapper(core='The number is 5.')
        """
        return Wrapper(f(self.core))

    def map_to_awaitable(
        self, f: Callable[[_T_co], Awaitable[_T]]
    ) -> AwaitableWrapper[_T]:
        """Apply an asynchronous function to the wrapped object.

        Args:
            f: The asynchronous function to be applied.

        Returns:
            An `AwaitableWrapper` instance with the result of the function application.

        Example:
            >>> import asyncio
            >>> from trcks.oop import Wrapper
            >>> async def stringify_slowly(o: object) -> str:
            ...     await asyncio.sleep(0.001)
            ...     return str(o)
            ...
            >>> awaitable_wrapper = Wrapper.construct(3.14).map_to_awaitable(
            ...     stringify_slowly
            ... )
            >>> awaitable_wrapper
            AwaitableWrapper(core=<coroutine object stringify_slowly at 0x...>)
            >>> asyncio.run(awaitable_wrapper.core_as_coroutine)
            '3.14'
        """
        return AwaitableWrapper(f(self.core))

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
            >>> from trcks.oop import Wrapper
            >>> async def slowly_assert_non_negative(
            ...     x: float,
            ... ) -> Result[str, float]:
            ...     await asyncio.sleep(0.001)
            ...     if x < 0:
            ...         return ("failure", "negative value")
            ...     return ("success", x)
            ...
            >>> awaitable_result_wrapper = (
            ...     Wrapper
            ...     .construct(42.0)
            ...     .map_to_awaitable_result(slowly_assert_non_negative)
            ... )
            >>> awaitable_result_wrapper
            AwaitableResultWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_result_wrapper.core_as_coroutine)
            ('success', 42.0)
        """
        return AwaitableResultWrapper(f(self.core))

    def map_to_result(
        self, f: Callable[[_T_co], Result[_F, _S]]
    ) -> ResultWrapper[_F, _S]:
        """Apply a sync. function with ret. type `trcks.Result` to the wrapped object.

        Args:
            f: The synchronous function to be applied.

        Returns:
            A `ResultWrapper` instance with the result of the function application.

        Example:
            >>> Wrapper.construct(-1).map_to_result(
            ...     lambda x: ("success", x)
            ...     if x >= 0
            ...     else ("failure", "negative value")
            ... )
            ResultWrapper(core=('failure', 'negative value'))
        """
        return ResultWrapper(f(self.core))
