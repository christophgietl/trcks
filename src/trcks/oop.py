"""Object-oriented interface for [trcks][].

This module provides wrapper classes for processing values of the following types
in a method-chaining style:

- [collections.abc.Awaitable][]
- [trcks.AwaitableResult][]
- [trcks.AwaitableResultTuple][]
- [trcks.AwaitableTuple][]
- [trcks.Result][]
- [trcks.ResultTuple][]
- [tuple][]

Example:
    This example uses the classes [trcks.oop.Wrapper][] and [trcks.oop.ResultWrapper][]
    to create and further process a value of type [trcks.Result][]:

    >>> import enum
    >>> import math
    >>> from trcks import Result
    >>> from trcks.oop import Wrapper
    >>> class GetSquareRootError(enum.Enum):
    ...     NEGATIVE_INPUT = enum.auto()
    ...
    >>> def get_square_root(x: float) -> Result[GetSquareRootError, float]:
    ...     return (
    ...         Wrapper(core=x)
    ...         .map_to_result(
    ...             lambda xx: ("success", xx)
    ...             if xx >= 0
    ...             else ("failure", GetSquareRootError.NEGATIVE_INPUT)
    ...         )
    ...         .map_success(math.sqrt)
    ...         .core
    ...     )
    ...
    >>> get_square_root(25.0)
    ('success', 5.0)
    >>> get_square_root(-25.0)
    ('failure', <GetSquareRootError.NEGATIVE_INPUT: 1>)

    Variable and type assignments for intermediate values might help to clarify
    what is going on:

    >>> import enum
    >>> import math
    >>> from trcks import Result
    >>> from trcks.oop import ResultWrapper, Wrapper
    >>> class GetSquareRootError(enum.Enum):
    ...     NEGATIVE_INPUT = enum.auto()
    ...
    >>> def get_square_root(x: float) -> Result[GetSquareRootError, float]:
    ...     wrapper: Wrapper[float] = Wrapper(core=x)
    ...     result_wrapper: ResultWrapper[
    ...         GetSquareRootError, float
    ...     ] = wrapper.map_to_result(
    ...         lambda xx: ("success", xx)
    ...         if xx >= 0
    ...         else ("failure", GetSquareRootError.NEGATIVE_INPUT)
    ...     )
    ...     mapped_result_wrapper: ResultWrapper[GetSquareRootError, float] = (
    ...         result_wrapper.map_success(math.sqrt)
    ...     )
    ...     result: Result[GetSquareRootError, float] = mapped_result_wrapper.core
    ...     return result
    ...
    >>> get_square_root(25.0)
    ('success', 5.0)
    >>> get_square_root(-25.0)
    ('failure', <GetSquareRootError.NEGATIVE_INPUT: 1>)

See:
    - [Method chaining - Wikipedia](https://en.wikipedia.org/w/index.php?title=Method_chaining&oldid=1262555147)
    - [Method Chaining in Python - GeeksforGeeks](https://www.geeksforgeeks.org/method-chaining-in-python/)
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Generic, Literal

from trcks import (
    AwaitableResult,
    AwaitableResultTuple,
    AwaitableTuple,
    Result,
    ResultTuple,
)
from trcks._typing import Never, TypeVar, override
from trcks.fp.monads import awaitable as a
from trcks.fp.monads import awaitable_result as ar
from trcks.fp.monads import awaitable_result_tuple as art
from trcks.fp.monads import awaitable_tuple as at
from trcks.fp.monads import identity as i
from trcks.fp.monads import result as r
from trcks.fp.monads import result_tuple as rt
from trcks.fp.monads import tuple_ as t

__docformat__ = "google"

_F = TypeVar("_F")
_S = TypeVar("_S")
_T = TypeVar("_T")

_T_co = TypeVar("_T_co", covariant=True)

_F_default = TypeVar("_F_default", default=Never)
_S_default = TypeVar("_S_default", default=Never)

_F_default_co = TypeVar("_F_default_co", covariant=True, default=Never)
_S_default_co = TypeVar("_S_default_co", covariant=True, default=Never)


class _Wrapper(Generic[_T_co]):
    """Base class for all wrappers in the [trcks.oop][] module.

    Attributes:
        __slots__: Attribute names to be used.
    """

    __slots__ = ("_core",)

    def __init__(self, core: _T_co) -> None:
        """Construct wrapper.

        Args:
            core: The value to be wrapped.
        """
        super().__init__()
        self._core: _T_co = core

    @override
    def __repr__(self) -> str:
        """Return a string representation of the wrapper."""
        return f"{self.__class__.__name__}(core={self._core!r})"

    @property
    def core(self) -> _T_co:
        """The wrapped value."""
        return self._core


class _AwaitableWrapper(_Wrapper[Awaitable[_T_co]]):
    """Base class for all asynchronous wrappers in the [trcks.oop][] module."""

    @property
    async def core_as_coroutine(self) -> _T_co:
        """The wrapped [collections.abc.Awaitable][] object
        transformed into a coroutine.

        This is useful for functions that expect a coroutine (e.g. [asyncio.run][]).

        Note:
            The attribute [trcks.oop._AwaitableWrapper.core][]
            has type [collections.abc.Awaitable][],
            a superclass of [collections.abc.Coroutine][].
        """
        return await self.core


class _AwaitableResultWrapper(_AwaitableWrapper[Result[_F_default_co, _S_default_co]]):
    """Base class for all awaitable result wrappers in the [trcks.oop][] module."""

    @property
    async def track(self) -> Literal["failure", "success"]:
        """First element of the awaited [trcks.Result][] object.

        Returns:
            The literal string `"failure"` or `"success"`.
        """
        return (await self.core)[0]

    @property
    async def value(self) -> _F_default_co | _S_default_co:
        """Second element of the awaited [trcks.Result][] object.

        Returns:
            The failure or success value.
        """
        return (await self.core)[1]


class _ResultWrapper(_Wrapper[Result[_F_default_co, _S_default_co]]):
    """Base class for all result wrappers in the [trcks.oop][] module."""

    @property
    def track(self) -> Literal["failure", "success"]:
        """First element of the wrapped [trcks.Result][] object.

        Returns:
            The literal string `"failure"` or `"success"`.
        """
        return self.core[0]

    @property
    def value(self) -> _F_default_co | _S_default_co:
        """Second element of the wrapped [trcks.Result][] object.

        Returns:
            The failure or success value.
        """
        return self.core[1]


class AwaitableResultTupleWrapper(
    _AwaitableResultWrapper[_F_default_co, tuple[_S_default_co, ...]]
):
    """Type-safe and immutable wrapper for [trcks.AwaitableResultTuple][] objects.

    The wrapped object can be accessed
    via the attribute `trcks.oop.AwaitableResultTupleWrapper.core`.
    The `trcks.oop.AwaitableResultTupleWrapper.map*` methods allow method chaining.
    The `trcks.oop.AwaitableResultTupleWrapper.tap*` methods allow for side effects
    without changing the wrapped [trcks.ResultTuple][].

    Example:
        >>> import asyncio
        >>> from trcks import Result
        >>> from trcks.oop import AwaitableResultTupleWrapper
        >>> async def read_from_disk() -> Result[str, int]:
        ...     await asyncio.sleep(0.001)
        ...     return "success", 3
        ...
        >>> async def main() -> Result[str, tuple[int, ...]]:
        ...     return await (
        ...         AwaitableResultTupleWrapper
        ...         .construct_from_awaitable_result(read_from_disk())
        ...         .map_successes(lambda n: n * 2)
        ...         .tap_successes(lambda n: print(f"Processed: {n}"))
        ...         .map_successes_to_tuple(lambda n: (n, -n))
        ...         .core
        ...     )
        ...
        >>> asyncio.run(main())
        Processed: 6
        ('success', (6, -6))
    """

    @staticmethod
    def construct_failure(value: _F) -> AwaitableResultTupleWrapper[_F, Never]:
        """Construct and wrap an awaitable [trcks.Failure][] object from a value.

        Args:
            value: The value to be wrapped.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with
                the wrapped [trcks.AwaitableResultTuple][] object.

        Example:
            >>> import asyncio
            >>> from trcks.oop import AwaitableResultTupleWrapper
            >>> wrapper = AwaitableResultTupleWrapper.construct_failure("not found")
            >>> wrapper
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper.core_as_coroutine)
            ('failure', 'not found')
        """
        return AwaitableResultTupleWrapper(art.construct_failure(value))

    @staticmethod
    def construct_failure_from_awaitable(
        awtbl: Awaitable[_F],
    ) -> AwaitableResultTupleWrapper[_F, Never]:
        """Construct and wrap an awaitable [trcks.Failure][] from an awaitable value.

        Args:
            awtbl: The awaitable value to be wrapped.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with
                the wrapped [trcks.AwaitableResultTuple][] object.

        Example:
            >>> import asyncio
            >>> from trcks.oop import AwaitableResultTupleWrapper
            >>> async def get_error() -> str:
            ...     await asyncio.sleep(0.001)
            ...     return "not found"
            ...
            >>> wrapper = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_failure_from_awaitable(get_error())
            ... )
            >>> wrapper
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper.core_as_coroutine)
            ('failure', 'not found')
        """
        return AwaitableResultTupleWrapper(art.construct_failure_from_awaitable(awtbl))

    @staticmethod
    def construct_from_awaitable_result(
        a_rslt: AwaitableResult[_F, _S],
    ) -> AwaitableResultTupleWrapper[_F, _S]:
        """Construct and wrap an [trcks.AwaitableResultTuple][] from an
        [trcks.AwaitableResult][].

        The success payload is wrapped in a single-element tuple.

        Args:
            a_rslt: The [trcks.AwaitableResult][] object to be converted.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance where
                the success payload is wrapped in a single-element tuple,
                or the original failure is preserved.

        Example:
            >>> import asyncio
            >>> from trcks.fp.monads import awaitable_result as ar
            >>> from trcks.oop import AwaitableResultTupleWrapper
            >>> wrapper_1 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_from_awaitable_result(ar.construct_success(7))
            ... )
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('success', (7,))
            >>>
            >>> wrapper_2 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_from_awaitable_result(ar.construct_failure("oops"))
            ... )
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('failure', 'oops')
        """
        return AwaitableResultTupleWrapper(art.construct_from_awaitable_result(a_rslt))

    @staticmethod
    def construct_from_result(
        rslt: Result[_F_default, _S_default],
    ) -> AwaitableResultTupleWrapper[_F_default, _S_default]:
        """Construct and wrap an [trcks.AwaitableResultTuple][] from a
        [trcks.Result][].

        The success payload is wrapped in a single-element tuple.

        Args:
            rslt: The [trcks.Result][] object to be converted.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance where
                the success payload is wrapped in a single-element tuple,
                or the original failure is preserved.

        Example:
            >>> import asyncio
            >>> from trcks.oop import AwaitableResultTupleWrapper
            >>> wrapper_1 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_from_result(("success", 7))
            ... )
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('success', (7,))
            >>>
            >>> wrapper_2 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_from_result(("failure", "oops"))
            ... )
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('failure', 'oops')
        """
        return AwaitableResultTupleWrapper(art.construct_from_result(rslt))

    @staticmethod
    def construct_from_result_tuple(
        rslt_tpl: ResultTuple[_F_default, _S_default],
    ) -> AwaitableResultTupleWrapper[_F_default, _S_default]:
        """Wrap a [trcks.ResultTuple][] object.

        Args:
            rslt_tpl: The [trcks.ResultTuple][] object to be wrapped.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with
                the wrapped [trcks.AwaitableResultTuple][] object.

        Example:
            >>> import asyncio
            >>> from trcks.oop import AwaitableResultTupleWrapper
            >>> wrapper = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_from_result_tuple(("success", (1, 2)))
            ... )
            >>> wrapper
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper.core_as_coroutine)
            ('success', (1, 2))
        """
        return AwaitableResultTupleWrapper(art.construct_from_result_tuple(rslt_tpl))

    @staticmethod
    def construct_successes(value: _S) -> AwaitableResultTupleWrapper[Never, _S]:
        """Construct and wrap an awaitable [trcks.SuccessTuple][] from a value.

        Args:
            value: The value to be wrapped in a single-element tuple.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with
                the wrapped [trcks.AwaitableResultTuple][] object.

        Example:
            >>> import asyncio
            >>> from trcks.oop import AwaitableResultTupleWrapper
            >>> wrapper = AwaitableResultTupleWrapper.construct_successes(42)
            >>> wrapper
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper.core_as_coroutine)
            ('success', (42,))
        """
        return AwaitableResultTupleWrapper(art.construct_successes(value))

    @staticmethod
    def construct_successes_from_awaitable(
        awtbl: Awaitable[_S],
    ) -> AwaitableResultTupleWrapper[Never, _S]:
        """Construct and wrap an awaitable [trcks.SuccessTuple][] from an
        awaitable value.

        Args:
            awtbl: The awaitable value to be wrapped in a single-element tuple.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with
                the wrapped [trcks.AwaitableResultTuple][] object.

        Example:
            >>> import asyncio
            >>> from trcks.oop import AwaitableResultTupleWrapper
            >>> async def read_value() -> int:
            ...     await asyncio.sleep(0.001)
            ...     return 7
            ...
            >>> wrapper = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_successes_from_awaitable(read_value())
            ... )
            >>> wrapper
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper.core_as_coroutine)
            ('success', (7,))
        """
        return AwaitableResultTupleWrapper(
            art.construct_successes_from_awaitable(awtbl)
        )

    @staticmethod
    def construct_successes_from_tuple(
        tpl: tuple[_S, ...],
    ) -> AwaitableResultTupleWrapper[Never, _S]:
        """Construct and wrap an awaitable [trcks.SuccessTuple][] from a tuple.

        Args:
            tpl: The tuple to be wrapped.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with
                the wrapped [trcks.AwaitableResultTuple][] object.

        Example:
            >>> import asyncio
            >>> from trcks.oop import AwaitableResultTupleWrapper
            >>> wrapper = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_successes_from_tuple((1, 2))
            ... )
            >>> wrapper
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper.core_as_coroutine)
            ('success', (1, 2))
        """
        return AwaitableResultTupleWrapper(art.construct_successes_from_tuple(tpl))

    def map_failure(
        self, f: Callable[[_F_default_co], _F]
    ) -> AwaitableResultTupleWrapper[_F, _S_default_co]:
        """Apply a synchronous function to the wrapped [trcks.Failure][] object.

        Wrapped [trcks.SuccessTuple][] objects are passed on unchanged.

        Args:
            f: The synchronous function to be applied.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - the result of the function application if
                    the original [trcks.AwaitableResultTuple][] is a failure, or
                - the original [trcks.AwaitableResultTuple][] if it is a success.

        Example:
            >>> import asyncio
            >>> from trcks.oop import AwaitableResultTupleWrapper
            >>> wrapper_1 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_failure("not found")
            ...     .map_failure(lambda e: f"err: {e}")
            ... )
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('failure', 'err: not found')
            >>>
            >>> wrapper_2 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_successes_from_tuple((1, 2))
            ...     .map_failure(lambda e: f"err: {e}")
            ... )
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('success', (1, 2))
        """
        return AwaitableResultTupleWrapper(art.map_failure(f)(self.core))

    def map_failure_to_awaitable(
        self, f: Callable[[_F_default_co], Awaitable[_F]]
    ) -> AwaitableResultTupleWrapper[_F, _S_default_co]:
        """Apply an asynchronous function to the wrapped [trcks.Failure][] object.

        Wrapped [trcks.SuccessTuple][] objects are passed on unchanged.

        Args:
            f: The asynchronous function to be applied.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - the result of the function application if
                    the original [trcks.AwaitableResultTuple][] is a failure, or
                - the original [trcks.AwaitableResultTuple][] if it is a success.

        Example:
            >>> import asyncio
            >>> from trcks.oop import AwaitableResultTupleWrapper
            >>> async def _slowly_add_prefix(s: str) -> str:
            ...     await asyncio.sleep(0.001)
            ...     return f"err: {s}"
            ...
            >>> wrapper_1 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_failure("not found")
            ...     .map_failure_to_awaitable(_slowly_add_prefix)
            ... )
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('failure', 'err: not found')
            >>>
            >>> wrapper_2 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_successes_from_tuple((1, 2))
            ...     .map_failure_to_awaitable(_slowly_add_prefix)
            ... )
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('success', (1, 2))
        """
        return AwaitableResultTupleWrapper(art.map_failure_to_awaitable(f)(self.core))

    def map_failure_to_awaitable_result_tuple(
        self, f: Callable[[_F_default_co], AwaitableResultTuple[_F, _S]]
    ) -> AwaitableResultTupleWrapper[_F, _S_default_co | _S]:
        """Apply an asynchronous function with return type
        [trcks.AwaitableResultTuple][] to the wrapped [trcks.Failure][] object.

        Wrapped [trcks.SuccessTuple][] objects are passed on unchanged.

        Args:
            f: The asynchronous function to be applied.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - the result of the function application if
                    the original [trcks.AwaitableResultTuple][] is a failure, or
                - the original [trcks.AwaitableResultTuple][] if it is a success.

        Example:
            >>> import asyncio
            >>> from trcks import ResultTuple
            >>> from trcks.oop import AwaitableResultTupleWrapper
            >>> async def _slowly_recover_from_not_found(
            ...     e: str,
            ... ) -> ResultTuple[str, int]:
            ...     await asyncio.sleep(0.001)
            ...     if e == "not found":
            ...         return "success", (0,)
            ...     return "failure", e
            ...
            >>> wrapper_1 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_failure("not found")
            ...     .map_failure_to_awaitable_result_tuple(
            ...         _slowly_recover_from_not_found,
            ...     )
            ... )
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('success', (0,))
            >>>
            >>> wrapper_2 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_failure("fatal")
            ...     .map_failure_to_awaitable_result_tuple(
            ...         _slowly_recover_from_not_found,
            ...     )
            ... )
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('failure', 'fatal')
            >>>
            >>> wrapper_3 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_successes_from_tuple((1, 2))
            ...     .map_failure_to_awaitable_result_tuple(
            ...         _slowly_recover_from_not_found,
            ...     )
            ... )
            >>> wrapper_3
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_3.core_as_coroutine)
            ('success', (1, 2))
        """
        return AwaitableResultTupleWrapper(
            art.map_failure_to_awaitable_result_tuple(f)(self.core)
        )

    def map_failure_to_result(
        self, f: Callable[[_F_default_co], Result[_F, _S]]
    ) -> AwaitableResultTupleWrapper[_F, _S_default_co | _S]:
        """Apply a synchronous function with return type [trcks.Result][]
        to the wrapped [trcks.Failure][] object.

        Wrapped [trcks.SuccessTuple][] objects are passed on unchanged.

        Args:
            f: The synchronous function to be applied.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - the result of the function application if
                    the original [trcks.AwaitableResultTuple][] is a failure, or
                - the original [trcks.AwaitableResultTuple][] if it is a success.

        Example:
            >>> import asyncio
            >>> from trcks import Result
            >>> from trcks.oop import AwaitableResultTupleWrapper
            >>> def _recover_from_not_found(description: str) -> Result[str, int]:
            ...     if description == "not found":
            ...         return "success", 0
            ...     return "failure", description
            ...
            >>> wrapper_1 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_failure("not found")
            ...     .map_failure_to_result(_recover_from_not_found)
            ... )
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('success', (0,))
            >>>
            >>> wrapper_2 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_failure("fatal")
            ...     .map_failure_to_result(_recover_from_not_found)
            ... )
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('failure', 'fatal')
            >>>
            >>> wrapper_3 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_successes_from_tuple((1, 2))
            ...     .map_failure_to_result(_recover_from_not_found)
            ... )
            >>> wrapper_3
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_3.core_as_coroutine)
            ('success', (1, 2))
        """
        return AwaitableResultTupleWrapper(art.map_failure_to_result(f)(self.core))

    def map_failure_to_result_tuple(
        self, f: Callable[[_F_default_co], ResultTuple[_F, _S]]
    ) -> AwaitableResultTupleWrapper[_F, _S_default_co | _S]:
        """Apply a synchronous function with return type [trcks.ResultTuple][]
        to the wrapped [trcks.Failure][] object.

        Wrapped [trcks.SuccessTuple][] objects are passed on unchanged.

        Args:
            f: The synchronous function to be applied.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - the result of the function application if
                    the original [trcks.AwaitableResultTuple][] is a failure, or
                - the original [trcks.AwaitableResultTuple][] if it is a success.

        Example:
            >>> import asyncio
            >>> from trcks import ResultTuple
            >>> from trcks.oop import AwaitableResultTupleWrapper
            >>> def _recover_from_not_found(description: str) -> ResultTuple[str, int]:
            ...     if description == "not found":
            ...         return "success", (0,)
            ...     return "failure", description
            ...
            >>> wrapper_1 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_failure("not found")
            ...     .map_failure_to_result_tuple(_recover_from_not_found)
            ... )
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('success', (0,))
            >>>
            >>> wrapper_2 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_failure("fatal")
            ...     .map_failure_to_result_tuple(_recover_from_not_found)
            ... )
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('failure', 'fatal')
            >>>
            >>> wrapper_3 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_successes_from_tuple((1, 2))
            ...     .map_failure_to_result_tuple(_recover_from_not_found)
            ... )
            >>> wrapper_3
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_3.core_as_coroutine)
            ('success', (1, 2))
        """
        return AwaitableResultTupleWrapper(
            art.map_failure_to_result_tuple(f)(self.core)
        )

    def map_failure_to_tuple(
        self, f: Callable[[_F_default_co], tuple[_S, ...]]
    ) -> AwaitableResultTupleWrapper[Never, _S_default_co | _S]:
        """Apply a synchronous function returning a tuple
        to the wrapped [trcks.Failure][] object.

        Wrapped [trcks.SuccessTuple][] objects are passed on unchanged.

        Args:
            f: The synchronous function returning a tuple to be applied.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - an [trcks.AwaitableSuccessTuple][] containing the result of
                    the function application if
                    the original [trcks.AwaitableResultTuple][] is a failure, or
                - the original [trcks.AwaitableResultTuple][] if it is a success.

        Example:
            >>> import asyncio
            >>> from trcks.oop import AwaitableResultTupleWrapper
            >>> def _recover_from_not_found(description: str) -> tuple[int, ...]:
            ...     if description == "not found":
            ...         return (0,)
            ...     return ()
            ...
            >>> wrapper_1 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_failure("not found")
            ...     .map_failure_to_tuple(_recover_from_not_found)
            ... )
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('success', (0,))
            >>>
            >>> wrapper_2 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_failure("fatal")
            ...     .map_failure_to_tuple(_recover_from_not_found)
            ... )
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('success', ())
            >>>
            >>> wrapper_3 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_successes_from_tuple((1, 2))
            ...     .map_failure_to_tuple(_recover_from_not_found)
            ... )
            >>> wrapper_3
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_3.core_as_coroutine)
            ('success', (1, 2))
        """
        mapped_f: Callable[
            [AwaitableResultTuple[_F_default_co, _S_default_co]],
            AwaitableResultTuple[Never, _S_default_co | _S],
        ] = art.map_failure_to_tuple(f)
        return AwaitableResultTupleWrapper(mapped_f(self.core))

    def map_successes(
        self, f: Callable[[_S_default_co], _S]
    ) -> AwaitableResultTupleWrapper[_F_default_co, _S]:
        """Apply a synchronous function to each element in the wrapped
        [trcks.AwaitableSuccessTuple][].

        Wrapped [trcks.Failure][] objects are passed on unchanged.

        Args:
            f: The synchronous function to be applied to each success element.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - the original [trcks.AwaitableResultTuple][] if it is a failure,
                    or
                - an [trcks.AwaitableSuccessTuple][] with transformed elements if
                    the original [trcks.AwaitableResultTuple][] is a success.

        Example:
            >>> import asyncio
            >>> from trcks.oop import AwaitableResultTupleWrapper
            >>> wrapper_1 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_successes_from_tuple((1, 2, 3))
            ...     .map_successes(lambda n: n * 2)
            ... )
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('success', (2, 4, 6))
            >>>
            >>> wrapper_2 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_failure("not found")
            ...     .map_successes(lambda n: n * 2)
            ... )
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('failure', 'not found')
        """
        return AwaitableResultTupleWrapper(art.map_successes(f)(self.core))

    def map_successes_to_awaitable(
        self, f: Callable[[_S_default_co], Awaitable[_S]]
    ) -> AwaitableResultTupleWrapper[_F_default_co, _S]:
        """Apply an asynchronous function to each element in the wrapped
        [trcks.AwaitableSuccessTuple][].

        Wrapped [trcks.Failure][] objects are passed on unchanged.

        Args:
            f: The asynchronous function to be applied to each success element.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - the original [trcks.AwaitableResultTuple][] if it is a failure,
                    or
                - an [trcks.AwaitableSuccessTuple][] with transformed elements if
                    the original [trcks.AwaitableResultTuple][] is a success.

        Example:
            >>> import asyncio
            >>> from trcks.oop import AwaitableResultTupleWrapper
            >>> async def _slowly_double_integer(n: int) -> int:
            ...     await asyncio.sleep(0.001)
            ...     return n * 2
            ...
            >>> wrapper_1 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_successes_from_tuple((1, 2, 3))
            ...     .map_successes_to_awaitable(_slowly_double_integer)
            ... )
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('success', (2, 4, 6))
            >>>
            >>> wrapper_2 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_failure("not found")
            ...     .map_successes_to_awaitable(_slowly_double_integer)
            ... )
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('failure', 'not found')
        """
        return AwaitableResultTupleWrapper(art.map_successes_to_awaitable(f)(self.core))

    def map_successes_to_awaitable_result(
        self, f: Callable[[_S_default_co], AwaitableResult[_F, _S]]
    ) -> AwaitableResultTupleWrapper[_F_default_co | _F, _S]:
        """Apply an asynchronous function with return type [trcks.AwaitableResult][]
        to each element in the wrapped [trcks.AwaitableSuccessTuple][].

        Wrapped [trcks.Failure][] objects are passed on unchanged.
        Short-circuits on the first failure returned by the function.

        Args:
            f: The asynchronous function to be applied to each success element.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - the original [trcks.AwaitableResultTuple][] if it is a failure,
                - the first [trcks.Failure][] returned by the function, or
                - an [trcks.AwaitableSuccessTuple][] with all transformed
                    elements if the function returns success for all elements.

        Example:
            >>> import asyncio
            >>> from trcks import Result
            >>> from trcks.oop import AwaitableResultTupleWrapper
            >>> async def _slowly_double_integer_if_positive(
            ...     n: int,
            ... ) -> Result[str, int]:
            ...     await asyncio.sleep(0.001)
            ...     if n <= 0:
            ...         return "failure", "negative"
            ...     return "success", n * 2
            ...
            >>> wrapper_1 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_successes_from_tuple((1, 2))
            ...     .map_successes_to_awaitable_result(
            ...         _slowly_double_integer_if_positive,
            ...     )
            ... )
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('success', (2, 4))
            >>>
            >>> wrapper_2 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_successes_from_tuple((1, -1, 2))
            ...     .map_successes_to_awaitable_result(
            ...         _slowly_double_integer_if_positive,
            ...     )
            ... )
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('failure', 'negative')
            >>>
            >>> wrapper_3 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_failure("oops")
            ...     .map_successes_to_awaitable_result(
            ...         _slowly_double_integer_if_positive,
            ...     )
            ... )
            >>> wrapper_3
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_3.core_as_coroutine)
            ('failure', 'oops')
        """
        return AwaitableResultTupleWrapper(
            art.map_successes_to_awaitable_result(f)(self.core)
        )

    def map_successes_to_awaitable_result_tuple(
        self, f: Callable[[_S_default_co], AwaitableResultTuple[_F, _S]]
    ) -> AwaitableResultTupleWrapper[_F_default_co | _F, _S]:
        """Apply an asynchronous function with return type
        [trcks.AwaitableResultTuple][] to each element in the wrapped
        [trcks.AwaitableSuccessTuple][] and flatten.

        Wrapped [trcks.Failure][] objects are passed on unchanged.
        Short-circuits on the first failure returned by the function.

        Args:
            f: The asynchronous function to be applied to each success element.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - the original [trcks.AwaitableResultTuple][] if it is a failure,
                - the first [trcks.Failure][] returned by the function, or
                - a flattened [trcks.AwaitableSuccessTuple][] if the function
                    returns success for all elements.

        Example:
            >>> import asyncio
            >>> from trcks import ResultTuple
            >>> from trcks.oop import AwaitableResultTupleWrapper
            >>> async def _slowly_duplicate_integer_if_positive(
            ...     n: int,
            ... ) -> ResultTuple[str, int]:
            ...     await asyncio.sleep(0.001)
            ...     if n <= 0:
            ...         return "failure", "negative"
            ...     return "success", (n, n)
            ...
            >>> wrapper_1 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_successes_from_tuple((1, 2))
            ...     .map_successes_to_awaitable_result_tuple(
            ...         _slowly_duplicate_integer_if_positive
            ...     )
            ... )
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('success', (1, 1, 2, 2))
            >>>
            >>> wrapper_2 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_successes_from_tuple((1, -1, 2))
            ...     .map_successes_to_awaitable_result_tuple(
            ...         _slowly_duplicate_integer_if_positive
            ...     )
            ... )
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('failure', 'negative')
            >>>
            >>> wrapper_3 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_failure("oops")
            ...     .map_successes_to_awaitable_result_tuple(
            ...         _slowly_duplicate_integer_if_positive
            ...     )
            ... )
            >>> wrapper_3
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_3.core_as_coroutine)
            ('failure', 'oops')
        """
        return AwaitableResultTupleWrapper(
            art.map_successes_to_awaitable_result_tuple(f)(self.core)
        )

    def map_successes_to_result(
        self, f: Callable[[_S_default_co], Result[_F, _S]]
    ) -> AwaitableResultTupleWrapper[_F_default_co | _F, _S]:
        """Apply a synchronous function with return type [trcks.Result][]
        to each element in the wrapped [trcks.AwaitableSuccessTuple][].

        Wrapped [trcks.Failure][] objects are passed on unchanged.
        Short-circuits on the first failure returned by the function.

        Args:
            f: The synchronous function to be applied to each success element.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - the original [trcks.AwaitableResultTuple][] if it is a failure,
                - the first [trcks.Failure][] returned by the function, or
                - an [trcks.AwaitableSuccessTuple][] with all transformed
                    elements if the function returns success for all elements.

        Example:
            >>> import asyncio
            >>> from trcks import Result
            >>> from trcks.oop import AwaitableResultTupleWrapper
            >>> def _double_integer_if_positive(n: int) -> Result[str, int]:
            ...     if n <= 0:
            ...         return "failure", "negative"
            ...     return "success", n * 2
            ...
            >>> wrapper_1 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_successes_from_tuple((1, 2))
            ...     .map_successes_to_result(_double_integer_if_positive)
            ... )
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('success', (2, 4))
            >>>
            >>> wrapper_2 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_successes_from_tuple((1, -1, 2))
            ...     .map_successes_to_result(_double_integer_if_positive)
            ... )
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('failure', 'negative')
            >>>
            >>> wrapper_3 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_failure("oops")
            ...     .map_successes_to_result(_double_integer_if_positive)
            ... )
            >>> wrapper_3
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_3.core_as_coroutine)
            ('failure', 'oops')
        """
        return AwaitableResultTupleWrapper(art.map_successes_to_result(f)(self.core))

    def map_successes_to_result_tuple(
        self, f: Callable[[_S_default_co], ResultTuple[_F, _S]]
    ) -> AwaitableResultTupleWrapper[_F_default_co | _F, _S]:
        """Apply a synchronous function with return type [trcks.ResultTuple][]
        to each element in the wrapped [trcks.AwaitableSuccessTuple][] and flatten.

        Wrapped [trcks.Failure][] objects are passed on unchanged.
        Short-circuits on the first failure returned by the function.

        Args:
            f: The synchronous function to be applied to each success element.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - the original [trcks.AwaitableResultTuple][] if it is a failure,
                - the first [trcks.Failure][] returned by the function, or
                - a flattened [trcks.AwaitableSuccessTuple][] if the function
                    returns success for all elements.

        Example:
            >>> import asyncio
            >>> from trcks import ResultTuple
            >>> from trcks.oop import AwaitableResultTupleWrapper
            >>> def _duplicate_integer_if_positive(n: int) -> ResultTuple[str, int]:
            ...     if n <= 0:
            ...         return "failure", "negative"
            ...     return "success", (n, n)
            ...
            >>> wrapper_1 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_successes_from_tuple((1, 2))
            ...     .map_successes_to_result_tuple(_duplicate_integer_if_positive)
            ... )
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('success', (1, 1, 2, 2))
            >>>
            >>> wrapper_2 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_failure("oops")
            ...     .map_successes_to_result_tuple(_duplicate_integer_if_positive)
            ... )
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('failure', 'oops')
        """
        return AwaitableResultTupleWrapper(
            art.map_successes_to_result_tuple(f)(self.core)
        )

    def map_successes_to_tuple(
        self, f: Callable[[_S_default_co], tuple[_S, ...]]
    ) -> AwaitableResultTupleWrapper[_F_default_co, _S]:
        """Apply a synchronous function returning a tuple to each element in
        the wrapped [trcks.AwaitableSuccessTuple][] and flatten.

        Wrapped [trcks.Failure][] objects are passed on unchanged.

        Args:
            f: The synchronous function to be applied to each success element.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - the original [trcks.AwaitableResultTuple][] if it is a failure,
                    or
                - a flattened [trcks.AwaitableSuccessTuple][] if
                    the original [trcks.AwaitableResultTuple][] is a success.

        Example:
            >>> import asyncio
            >>> from trcks.oop import AwaitableResultTupleWrapper
            >>> def _duplicate_integer(n: int) -> tuple[int, int]:
            ...     return n, n
            ...
            >>> wrapper_1 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_successes_from_tuple((1, 2))
            ...     .map_successes_to_tuple(_duplicate_integer)
            ... )
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('success', (1, 1, 2, 2))
        """
        return AwaitableResultTupleWrapper(art.map_successes_to_tuple(f)(self.core))

    def tap_failure(
        self, f: Callable[[_F_default_co], object]
    ) -> AwaitableResultTupleWrapper[_F_default_co, _S_default_co]:
        """Apply a synchronous side effect to the wrapped [trcks.Failure][] object.

        Wrapped [trcks.SuccessTuple][] objects are passed on without side effects.

        Args:
            f: The synchronous side effect to be applied.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance
                with the original [trcks.AwaitableResultTuple][] object,
                allowing for further method chaining.

        Example:
            >>> import asyncio
            >>> from trcks.oop import AwaitableResultTupleWrapper
            >>> def _log_failure(description: str) -> None:
            ...     print(f"Failure: {description}")
            ...
            >>> wrapper_1 = AwaitableResultTupleWrapper.construct_failure(
            ...     "oops"
            ... ).tap_failure(_log_failure)
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> result_1 = asyncio.run(wrapper_1.core_as_coroutine)
            Failure: oops
            >>> result_1
            ('failure', 'oops')
            >>> wrapper_2 = AwaitableResultTupleWrapper.construct_successes_from_tuple(
            ...     (1,)
            ... ).tap_failure(_log_failure)
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> result_2 = asyncio.run(wrapper_2.core_as_coroutine)
            >>> result_2
            ('success', (1,))
        """
        return AwaitableResultTupleWrapper(art.tap_failure(f)(self.core))

    def tap_failure_to_awaitable(
        self, f: Callable[[_F_default_co], Awaitable[object]]
    ) -> AwaitableResultTupleWrapper[_F_default_co, _S_default_co]:
        """Apply an asynchronous side effect to the wrapped [trcks.Failure][] object.

        Wrapped [trcks.SuccessTuple][] objects are passed on without side effects.

        Args:
            f: The asynchronous side effect to be applied.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance
                with the original [trcks.AwaitableResultTuple][] object,
                allowing for further method chaining.

        Example:
            >>> import asyncio
            >>> from trcks.oop import AwaitableResultTupleWrapper
            >>> async def _slowly_log_failure(e: str) -> None:
            ...     await asyncio.sleep(0.001)
            ...     print(f"Failure: {e}")
            ...
            >>> wrapper_1 = AwaitableResultTupleWrapper.construct_failure(
            ...     "oops"
            ... ).tap_failure_to_awaitable(_slowly_log_failure)
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> result_1 = asyncio.run(wrapper_1.core_as_coroutine)
            Failure: oops
            >>> result_1
            ('failure', 'oops')
            >>> wrapper_2 = AwaitableResultTupleWrapper.construct_successes_from_tuple(
            ...     (1,)
            ... ).tap_failure_to_awaitable(_slowly_log_failure)
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> result_2 = asyncio.run(wrapper_2.core_as_coroutine)
            >>> result_2
            ('success', (1,))
        """
        return AwaitableResultTupleWrapper(art.tap_failure_to_awaitable(f)(self.core))

    def tap_failure_to_awaitable_result(
        self, f: Callable[[_F_default_co], AwaitableResult[object, _S]]
    ) -> AwaitableResultTupleWrapper[_F_default_co, _S_default_co | _S]:
        """Apply an asynchronous side effect with return type [trcks.AwaitableResult][]
        to the wrapped [trcks.Failure][] object.

        Wrapped [trcks.SuccessTuple][] objects are passed on without side effects.

        Args:
            f: The asynchronous side effect to be applied.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - *the original* [trcks.Failure][]
                    if the applied side effect returns a [trcks.Failure][],
                - *the returned* [trcks.Success][] (wrapped as a tuple)
                    if the applied side effect returns a [trcks.Success][] and
                - *the original* [trcks.SuccessTuple][]
                    if no side effect was applied.

        Example:
            >>> import asyncio
            >>> from trcks import Result
            >>> from trcks.oop import AwaitableResultTupleWrapper
            >>> async def _slowly_recover_from_not_found(e: str) -> Result[str, int]:
            ...     await asyncio.sleep(0.001)
            ...     if e == "not found":
            ...         return "success", 0
            ...     return "failure", e
            ...
            >>> wrapper_1 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_failure("not found")
            ...     .tap_failure_to_awaitable_result(_slowly_recover_from_not_found)
            ... )
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('success', (0,))
            >>>
            >>> wrapper_2 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_failure("fatal")
            ...     .tap_failure_to_awaitable_result(_slowly_recover_from_not_found)
            ... )
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('failure', 'fatal')
        """
        return AwaitableResultTupleWrapper(
            art.tap_failure_to_awaitable_result(f)(self.core)
        )

    def tap_failure_to_awaitable_result_tuple(
        self, f: Callable[[_F_default_co], AwaitableResultTuple[object, _S]]
    ) -> AwaitableResultTupleWrapper[_F_default_co, _S_default_co | _S]:
        """Apply an asynchronous side effect with return type
        [trcks.AwaitableResultTuple][] to the wrapped [trcks.Failure][] object.

        Wrapped [trcks.SuccessTuple][] objects are passed on without side effects.

        Args:
            f: The asynchronous side effect to be applied.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - *the original* [trcks.Failure][]
                    if the applied side effect returns a [trcks.Failure][],
                - *the returned* [trcks.SuccessTuple][]
                    if the applied side effect returns a [trcks.SuccessTuple][] and
                - *the original* [trcks.SuccessTuple][]
                    if no side effect was applied.

        Example:
            >>> import asyncio
            >>> from trcks import ResultTuple
            >>> from trcks.oop import AwaitableResultTupleWrapper
            >>> async def _slowly_recover_from_not_found(
            ...     e: str,
            ... ) -> ResultTuple[str, int]:
            ...     await asyncio.sleep(0.001)
            ...     if e == "not found":
            ...         return "success", (0,)
            ...     return "failure", e
            ...
            >>> wrapper_1 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_failure("not found")
            ...     .tap_failure_to_awaitable_result_tuple(
            ...         _slowly_recover_from_not_found,
            ...     )
            ... )
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('success', (0,))
            >>>
            >>> wrapper_2 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_failure("fatal")
            ...     .tap_failure_to_awaitable_result_tuple(
            ...         _slowly_recover_from_not_found,
            ...     )
            ... )
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('failure', 'fatal')
        """
        return AwaitableResultTupleWrapper(
            art.tap_failure_to_awaitable_result_tuple(f)(self.core)
        )

    def tap_failure_to_result(
        self, f: Callable[[_F_default_co], Result[object, _S]]
    ) -> AwaitableResultTupleWrapper[_F_default_co, _S_default_co | _S]:
        """Apply a synchronous side effect with return type [trcks.Result][]
        to the wrapped [trcks.Failure][] object.

        Wrapped [trcks.SuccessTuple][] objects are passed on without side effects.

        Args:
            f: The synchronous side effect to be applied.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - *the original* [trcks.Failure][]
                    if the applied side effect returns a [trcks.Failure][],
                - *the returned* [trcks.Success][] (wrapped as a tuple)
                    if the applied side effect returns a [trcks.Success][] and
                - *the original* [trcks.SuccessTuple][]
                    if no side effect was applied.

        Example:
            >>> import asyncio
            >>> from trcks import Result
            >>> from trcks.oop import AwaitableResultTupleWrapper
            >>> def _recover_from_not_found(description: str) -> Result[None, int]:
            ...     if description == "not found":
            ...         return "success", 0
            ...     return "failure", None
            ...
            >>> wrapper_1 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_failure("not found")
            ...     .tap_failure_to_result(_recover_from_not_found)
            ... )
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('success', (0,))
            >>>
            >>> wrapper_2 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_failure("fatal")
            ...     .tap_failure_to_result(_recover_from_not_found)
            ... )
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('failure', 'fatal')
            >>>
            >>> wrapper_3 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_successes_from_tuple((1,))
            ...     .tap_failure_to_result(_recover_from_not_found)
            ... )
            >>> wrapper_3
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_3.core_as_coroutine)
            ('success', (1,))
        """
        return AwaitableResultTupleWrapper(art.tap_failure_to_result(f)(self.core))

    def tap_failure_to_result_tuple(
        self, f: Callable[[_F_default_co], ResultTuple[object, _S]]
    ) -> AwaitableResultTupleWrapper[_F_default_co, _S_default_co | _S]:
        """Apply a synchronous side effect with return type [trcks.ResultTuple][]
        to the wrapped [trcks.Failure][] object.

        Wrapped [trcks.SuccessTuple][] objects are passed on without side effects.

        Args:
            f: The synchronous side effect to be applied.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - *the original* [trcks.Failure][]
                    if the applied side effect returns a [trcks.Failure][],
                - *the returned* [trcks.SuccessTuple][]
                    if the applied side effect returns a [trcks.SuccessTuple][] and
                - *the original* [trcks.SuccessTuple][]
                    if no side effect was applied.

        Example:
            >>> import asyncio
            >>> from trcks import ResultTuple
            >>> from trcks.oop import AwaitableResultTupleWrapper
            >>> def _recover_from_not_found(description: str) -> ResultTuple[None, int]:
            ...     if description == "not found":
            ...         return "success", (0,)
            ...     return "failure", None
            ...
            >>> wrapper_1 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_failure("not found")
            ...     .tap_failure_to_result_tuple(_recover_from_not_found)
            ... )
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('success', (0,))
            >>>
            >>> wrapper_2 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_failure("fatal")
            ...     .tap_failure_to_result_tuple(_recover_from_not_found)
            ... )
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('failure', 'fatal')
            >>>
            >>> wrapper_3 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_successes_from_tuple((1,))
            ...     .tap_failure_to_result_tuple(_recover_from_not_found)
            ... )
            >>> wrapper_3
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_3.core_as_coroutine)
            ('success', (1,))
        """
        return AwaitableResultTupleWrapper(
            art.tap_failure_to_result_tuple(f)(self.core)
        )

    def tap_failure_to_tuple(
        self, f: Callable[[_F_default_co], tuple[object, ...]]
    ) -> AwaitableResultTupleWrapper[Never, _F_default_co | _S_default_co]:
        """Apply a synchronous side effect returning a tuple
        to the wrapped [trcks.Failure][] object.

        The failure is converted to an [trcks.AwaitableSuccessTuple][] where
        the original failure value is repeated once per element in
        the tuple returned by the side effect.

        Wrapped [trcks.SuccessTuple][] objects are passed on without side effects.

        Args:
            f: The synchronous side effect returning a tuple to be applied.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - an [trcks.AwaitableSuccessTuple][] containing the original
                    failure repeated once per element in the tuple returned by
                    the side effect if the original
                    [trcks.AwaitableResultTuple][] is a failure, or
                - the original [trcks.AwaitableSuccessTuple][]
                    if no side effect was applied.

        Example:
            >>> import asyncio
            >>> from trcks.oop import AwaitableResultTupleWrapper
            >>> def _log_and_alert(description: str) -> tuple[None, None]:
            ...     return (
            ...         print(f"Failure: {description}"),
            ...         print(f"Logged: {description}"),
            ...     )
            ...
            >>> wrapper_1 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_failure("critical")
            ...     .tap_failure_to_tuple(_log_and_alert)
            ... )
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> result_1 = asyncio.run(wrapper_1.core_as_coroutine)
            Failure: critical
            Logged: critical
            >>> result_1
            ('success', ('critical', 'critical'))
            >>>
            >>> wrapper_2 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_successes_from_tuple((1,))
            ...     .tap_failure_to_tuple(_log_and_alert)
            ... )
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('success', (1,))
        """
        tapped_f: Callable[
            [AwaitableResultTuple[_F_default_co, _S_default_co]],
            AwaitableResultTuple[Never, _F_default_co | _S_default_co],
        ] = art.tap_failure_to_tuple(f)
        return AwaitableResultTupleWrapper(tapped_f(self.core))

    def tap_successes(
        self, f: Callable[[_S_default_co], object]
    ) -> AwaitableResultTupleWrapper[_F_default_co, _S_default_co]:
        """Apply a synchronous side effect to each element in the wrapped
        [trcks.AwaitableSuccessTuple][].

        Wrapped [trcks.Failure][] objects are passed on without side effects.

        Args:
            f: The synchronous side effect to be applied to each success element.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance
                with the original [trcks.AwaitableResultTuple][] object,
                allowing for further method chaining.

        Example:
            >>> import asyncio
            >>> from trcks.oop import AwaitableResultTupleWrapper
            >>> def _log_value(n: int) -> None:
            ...     print(f"Value: {n}")
            ...
            >>> wrapper_1 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_successes_from_tuple((1, 2))
            ...     .tap_successes(_log_value)
            ... )
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> result_1 = asyncio.run(wrapper_1.core_as_coroutine)
            Value: 1
            Value: 2
            >>> result_1
            ('success', (1, 2))
            >>> wrapper_2 = AwaitableResultTupleWrapper.construct_failure(
            ...     "oops"
            ... ).tap_successes(_log_value)
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> result_2 = asyncio.run(wrapper_2.core_as_coroutine)
            >>> result_2
            ('failure', 'oops')
        """
        return AwaitableResultTupleWrapper(art.tap_successes(f)(self.core))

    def tap_successes_to_awaitable(
        self, f: Callable[[_S_default_co], Awaitable[object]]
    ) -> AwaitableResultTupleWrapper[_F_default_co, _S_default_co]:
        """Apply an asynchronous side effect to each element in the wrapped
        [trcks.AwaitableSuccessTuple][].

        Wrapped [trcks.Failure][] objects are passed on without side effects.

        Args:
            f: The asynchronous side effect to be applied to each success element.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance
                with the original [trcks.AwaitableResultTuple][] object,
                allowing for further method chaining.

        Example:
            >>> import asyncio
            >>> from trcks.oop import AwaitableResultTupleWrapper
            >>> async def _slowly_log_value(n: int) -> None:
            ...     await asyncio.sleep(0.001)
            ...     print(f"Value: {n}")
            ...
            >>> wrapper_1 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_successes_from_tuple((1, 2))
            ...     .tap_successes_to_awaitable(_slowly_log_value)
            ... )
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> result_1 = asyncio.run(wrapper_1.core_as_coroutine)
            Value: 1
            Value: 2
            >>> result_1
            ('success', (1, 2))
            >>> wrapper_2 = AwaitableResultTupleWrapper.construct_failure(
            ...     "oops"
            ... ).tap_successes_to_awaitable(_slowly_log_value)
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> result_2 = asyncio.run(wrapper_2.core_as_coroutine)
            >>> result_2
            ('failure', 'oops')
        """
        return AwaitableResultTupleWrapper(art.tap_successes_to_awaitable(f)(self.core))

    def tap_successes_to_awaitable_result(
        self, f: Callable[[_S_default_co], AwaitableResult[_F, object]]
    ) -> AwaitableResultTupleWrapper[_F_default_co | _F, _S_default_co]:
        """Apply an asynchronous side effect with return type [trcks.AwaitableResult][]
        to each element in the wrapped [trcks.AwaitableSuccessTuple][].

        Wrapped [trcks.Failure][] objects are passed on without side effects.

        Args:
            f: The asynchronous side effect to be applied to each success element.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - *the original* [trcks.Failure][] if no side effect was applied,
                - *the returned* [trcks.Failure][]
                    if the applied side effect returns a [trcks.Failure][] and
                - *the original* [trcks.AwaitableSuccessTuple][]
                    if the applied side effect returns success for all elements.

        Example:
            >>> import asyncio
            >>> from trcks import Result
            >>> from trcks.oop import AwaitableResultTupleWrapper
            >>> async def _validate_positive(n: int) -> Result[str, None]:
            ...     await asyncio.sleep(0.001)
            ...     if n <= 0:
            ...         return "failure", "negative"
            ...     return "success", None
            ...
            >>> wrapper_1 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_successes_from_tuple((1, 2))
            ...     .tap_successes_to_awaitable_result(_validate_positive)
            ... )
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('success', (1, 2))
            >>>
            >>> wrapper_2 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_successes_from_tuple((1, -1))
            ...     .tap_successes_to_awaitable_result(_validate_positive)
            ... )
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('failure', 'negative')
            >>>
            >>> wrapper_3 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_failure("oops")
            ...     .tap_successes_to_awaitable_result(_validate_positive)
            ... )
            >>> wrapper_3
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_3.core_as_coroutine)
            ('failure', 'oops')
        """
        return AwaitableResultTupleWrapper(
            art.tap_successes_to_awaitable_result(f)(self.core)
        )

    def tap_successes_to_awaitable_result_tuple(
        self, f: Callable[[_S_default_co], AwaitableResultTuple[_F, object]]
    ) -> AwaitableResultTupleWrapper[_F_default_co | _F, _S_default_co]:
        """Apply an asynchronous side effect with return type
        [trcks.AwaitableResultTuple][] to each element in the wrapped
        [trcks.AwaitableSuccessTuple][].

        Wrapped [trcks.Failure][] objects are passed on without side effects.

        Args:
            f: The asynchronous side effect to be applied to each success element.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - *the original* [trcks.Failure][] if no side effect was applied,
                - *the returned* [trcks.Failure][]
                    if the applied side effect returns a [trcks.Failure][] and
                - *the original* success element repeated once per element
                    in the side effect output if the applied side effect returns
                    success for all elements.

        Example:
            >>> import asyncio
            >>> from trcks import ResultTuple
            >>> from trcks.oop import AwaitableResultTupleWrapper
            >>> async def _validate_positive(n: int) -> ResultTuple[str, None]:
            ...     await asyncio.sleep(0.001)
            ...     if n <= 0:
            ...         return "failure", "negative"
            ...     return "success", (None, None)
            ...
            >>> wrapper_1 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_successes_from_tuple((7,))
            ...     .tap_successes_to_awaitable_result_tuple(_validate_positive)
            ... )
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('success', (7, 7))
            >>>
            >>> wrapper_2 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_successes_from_tuple((1, -1))
            ...     .tap_successes_to_awaitable_result_tuple(_validate_positive)
            ... )
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('failure', 'negative')
            >>>
            >>> wrapper_3 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_failure("oops")
            ...     .tap_successes_to_awaitable_result_tuple(_validate_positive)
            ... )
            >>> wrapper_3
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_3.core_as_coroutine)
            ('failure', 'oops')
        """
        return AwaitableResultTupleWrapper(
            art.tap_successes_to_awaitable_result_tuple(f)(self.core)
        )

    def tap_successes_to_result(
        self, f: Callable[[_S_default_co], Result[_F, object]]
    ) -> AwaitableResultTupleWrapper[_F_default_co | _F, _S_default_co]:
        """Apply a synchronous side effect with return type [trcks.Result][]
        to each element in the wrapped [trcks.AwaitableSuccessTuple][].

        Wrapped [trcks.Failure][] objects are passed on without side effects.

        Args:
            f: The synchronous side effect to be applied to each success element.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - *the original* [trcks.Failure][] if no side effect was applied,
                - *the returned* [trcks.Failure][]
                    if the applied side effect returns a [trcks.Failure][] and
                - *the original* [trcks.AwaitableSuccessTuple][]
                    if the applied side effect returns success for all elements.

        Example:
            >>> import asyncio
            >>> from trcks import Result
            >>> from trcks.oop import AwaitableResultTupleWrapper
            >>> def _validate_positive(n: int) -> Result[str, None]:
            ...     if n <= 0:
            ...         return "failure", "negative"
            ...     return "success", None
            ...
            >>> wrapper_1 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_successes_from_tuple((1, 2))
            ...     .tap_successes_to_result(_validate_positive)
            ... )
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('success', (1, 2))
            >>>
            >>> wrapper_2 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_successes_from_tuple((1, -1))
            ...     .tap_successes_to_result(_validate_positive)
            ... )
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('failure', 'negative')
            >>>
            >>> wrapper_3 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_failure("oops")
            ...     .tap_successes_to_result(_validate_positive)
            ... )
            >>> wrapper_3
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_3.core_as_coroutine)
            ('failure', 'oops')
        """
        return AwaitableResultTupleWrapper(art.tap_successes_to_result(f)(self.core))

    def tap_successes_to_result_tuple(
        self, f: Callable[[_S_default_co], ResultTuple[_F, object]]
    ) -> AwaitableResultTupleWrapper[_F_default_co | _F, _S_default_co]:
        """Apply a synchronous side effect with return type [trcks.ResultTuple][]
        to each element in the wrapped [trcks.AwaitableSuccessTuple][].

        Wrapped [trcks.Failure][] objects are passed on without side effects.

        Args:
            f: The synchronous side effect to be applied to each success element.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - *the original* [trcks.Failure][] if no side effect was applied,
                - *the returned* [trcks.Failure][]
                    if the applied side effect returns a [trcks.Failure][] and
                - *the original* success element repeated once per element
                    in the side effect output if the applied side effect returns
                    success for all elements.

        Example:
            >>> import asyncio
            >>> from trcks import ResultTuple
            >>> from trcks.oop import AwaitableResultTupleWrapper
            >>> def _validate_positive_twice(n: int) -> ResultTuple[str, None]:
            ...     if n <= 0:
            ...         return "failure", "negative"
            ...     return "success", (None, None)
            ...
            >>> wrapper_1 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_successes_from_tuple((7,))
            ...     .tap_successes_to_result_tuple(_validate_positive_twice)
            ... )
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('success', (7, 7))
            >>>
            >>> wrapper_2 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_successes_from_tuple((1, -1))
            ...     .tap_successes_to_result_tuple(_validate_positive_twice)
            ... )
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('failure', 'negative')
            >>>
            >>> wrapper_3 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_failure("oops")
            ...     .tap_successes_to_result_tuple(_validate_positive_twice)
            ... )
            >>> wrapper_3
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_3.core_as_coroutine)
            ('failure', 'oops')
        """
        return AwaitableResultTupleWrapper(
            art.tap_successes_to_result_tuple(f)(self.core)
        )

    def tap_successes_to_tuple(
        self, f: Callable[[_S_default_co], tuple[object, ...]]
    ) -> AwaitableResultTupleWrapper[_F_default_co, _S_default_co]:
        """Apply a synchronous side effect returning a tuple to each element in
        the wrapped [trcks.AwaitableSuccessTuple][].

        The original success elements are repeated once per element in the tuple
        returned by the side effect.

        Wrapped [trcks.Failure][] objects are passed on without side effects.

        Args:
            f: The synchronous side effect returning a tuple to be applied
                to each success element.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - the original [trcks.Failure][] if no side effect was applied, or
                - an [trcks.AwaitableSuccessTuple][] where each original element
                    is repeated once per element in the tuple returned by the
                    side effect.

        Example:
            >>> import asyncio
            >>> from trcks.oop import AwaitableResultTupleWrapper
            >>> def _log_twice(n: int) -> tuple[None, None]:
            ...     return print(f"Received: {n}"), print(f"Received: {n}")
            ...
            >>> wrapper_1 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_successes_from_tuple((7,))
            ...     .tap_successes_to_tuple(_log_twice)
            ... )
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> result_1 = asyncio.run(wrapper_1.core_as_coroutine)
            Received: 7
            Received: 7
            >>> result_1
            ('success', (7, 7))
        """
        return AwaitableResultTupleWrapper(art.tap_successes_to_tuple(f)(self.core))


class AwaitableResultWrapper(_AwaitableResultWrapper[_F_default_co, _S_default_co]):
    """Type-safe and immutable wrapper for [trcks.AwaitableResult][] objects.

    The wrapped object can be accessed
    via the attribute `trcks.oop.AwaitableResultWrapper.core`.
    The `trcks.oop.AwaitableResultWrapper.map*` methods allow method chaining.

    Example:
        >>> import asyncio
        >>> import math
        >>> from trcks import Result
        >>> from trcks.oop import AwaitableResultWrapper
        >>> async def read_from_disk() -> Result[str, float]:
        ...     await asyncio.sleep(0.001)
        ...     return "failure", "not found"
        ...
        >>> def get_square_root(x: float) -> Result[str, float]:
        ...     if x < 0:
        ...         return "failure", "negative value"
        ...     return "success", math.sqrt(x)
        ...
        >>> async def write_to_disk(output: float) -> None:
        ...     await asyncio.sleep(0.001)
        ...     print(f"Wrote '{output}' to disk.")
        ...
        >>> async def main() -> Result[str, None]:
        ...     awaitable_result = read_from_disk()
        ...     return await (
        ...         AwaitableResultWrapper
        ...         .construct_from_awaitable_result(awaitable_result)
        ...         .map_success_to_result(get_square_root)
        ...         .map_success_to_awaitable(write_to_disk)
        ...         .core
        ...     )
        ...
        >>> asyncio.run(main())
        ('failure', 'not found')
    """

    @staticmethod
    def construct_failure(value: _F) -> AwaitableResultWrapper[_F, Never]:
        """Construct and wrap an awaitable [trcks.Failure][] object from a value.

        Args:
            value: The value to be wrapped.

        Returns:
            A new [trcks.oop.AwaitableResultWrapper][] instance with
                the wrapped [trcks.AwaitableResult][] object.

        Example:
            >>> import asyncio
            >>> from trcks.oop import AwaitableResultWrapper
            >>> awaitable_result_wrapper = (
            ...     AwaitableResultWrapper.construct_failure("not found")
            ... )
            >>> awaitable_result_wrapper
            AwaitableResultWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_result_wrapper.core_as_coroutine)
            ('failure', 'not found')
        """
        return AwaitableResultWrapper(ar.construct_failure(value))

    @staticmethod
    def construct_failure_from_awaitable(
        awtbl: Awaitable[_F],
    ) -> AwaitableResultWrapper[_F, Never]:
        """Construct and wrap an awaitable [trcks.Failure][] from an awaitable value.

        Args:
            awtbl: The awaitable value to be wrapped.

        Returns:
            A new [trcks.oop.AwaitableResultWrapper][] instance with
                the wrapped [trcks.AwaitableResult][] object.

        Example:
            >>> import asyncio
            >>> from http import HTTPStatus
            >>> from trcks.oop import AwaitableResultWrapper
            >>> async def get_status() -> HTTPStatus:
            ...     await asyncio.sleep(0.001)
            ...     return HTTPStatus.NOT_FOUND
            ...
            >>> awaitable_status = get_status()
            >>> awaitable_result_wrapper = (
            ...     AwaitableResultWrapper
            ...     .construct_failure_from_awaitable(awaitable_status)
            ... )
            >>> awaitable_result_wrapper
            AwaitableResultWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_result_wrapper.core_as_coroutine)
            ('failure', <HTTPStatus.NOT_FOUND: 404>)
        """
        return AwaitableResultWrapper(ar.construct_failure_from_awaitable(awtbl))

    @staticmethod
    def construct_from_awaitable_result(
        a_rslt: AwaitableResult[_F, _S],
    ) -> AwaitableResultWrapper[_F, _S]:
        """Wrap an awaitable [trcks.Result][] object.

        Args:
            a_rslt: The awaitable [trcks.Result][] object to be wrapped.

        Returns:
            A new [trcks.oop.AwaitableResultWrapper][] instance with
                the wrapped [trcks.AwaitableResult][] object.

        Example:
            >>> import asyncio
            >>> from trcks import Result
            >>> from trcks.oop import AwaitableResultWrapper
            >>> async def read_from_disk() -> Result[str, str]:
            ...     await asyncio.sleep(0.001)
            ...     return "failure", "file not found"
            ...
            >>> awaitable_result = read_from_disk()
            >>> awaitable_wrapper = (
            ...     AwaitableResultWrapper
            ...     .construct_from_awaitable_result(awaitable_result)
            ... )
            >>> awaitable_wrapper
            AwaitableResultWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_wrapper.core_as_coroutine)
            ('failure', 'file not found')
        """
        return AwaitableResultWrapper(a_rslt)

    @staticmethod
    def construct_from_result(
        rslt: Result[_F_default, _S_default],
    ) -> AwaitableResultWrapper[_F_default, _S_default]:
        """Construct and wrap an awaitable [trcks.Result][] object
        from a [trcks.Result][] object.

        Args:
            rslt: The [trcks.Result][] object to be wrapped.

        Returns:
            A new [trcks.oop.AwaitableResultWrapper][] instance with
                the wrapped [trcks.AwaitableResult][] object.

        Example:
            >>> import asyncio
            >>> from trcks.oop import AwaitableResultWrapper
            >>> awaitable_result_wrapper = (
            ...     AwaitableResultWrapper
            ...     .construct_from_result(("failure", "not found"))
            ... )
            >>> awaitable_result_wrapper
            AwaitableResultWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_result_wrapper.core_as_coroutine)
            ('failure', 'not found')
        """
        return AwaitableResultWrapper(ar.construct_from_result(rslt))

    @staticmethod
    def construct_success(value: _S) -> AwaitableResultWrapper[Never, _S]:
        """Construct and wrap an awaitable [trcks.Success][] object from a value.

        Args:
            value: The value to be wrapped.

        Returns:
            A new [trcks.oop.AwaitableResultWrapper][] instance with
                the wrapped [trcks.AwaitableResult][] object.

        Example:
            >>> import asyncio
            >>> from trcks.oop import AwaitableResultWrapper
            >>> awaitable_result_wrapper = AwaitableResultWrapper.construct_success(42)
            >>> awaitable_result_wrapper
            AwaitableResultWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_result_wrapper.core_as_coroutine)
            ('success', 42)
        """
        return AwaitableResultWrapper(ar.construct_success(value))

    @staticmethod
    def construct_success_from_awaitable(
        awtbl: Awaitable[_S],
    ) -> AwaitableResultWrapper[Never, _S]:
        """Construct and wrap an awaitable [trcks.Success][] from an awaitable value.

        Args:
            awtbl: The awaitable value to be wrapped.

        Returns:
            A new [trcks.oop.AwaitableResultWrapper][] instance with
                the wrapped [trcks.AwaitableResult][] object.

        Example:
            >>> import asyncio
            >>> from trcks.oop import AwaitableResultWrapper
            >>> async def read_from_disk() -> str:
            ...     await asyncio.sleep(0.001)
            ...     return "Hello, world!"
            ...
            >>> awaitable_str = read_from_disk()
            >>> awaitable_result_wrapper = (
            ...     AwaitableResultWrapper
            ...     .construct_success_from_awaitable(awaitable_str)
            ... )
            >>> awaitable_result_wrapper
            AwaitableResultWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_result_wrapper.core_as_coroutine)
            ('success', 'Hello, world!')
        """
        return AwaitableResultWrapper(ar.construct_success_from_awaitable(awtbl))

    def map_failure(
        self, f: Callable[[_F_default_co], _F]
    ) -> AwaitableResultWrapper[_F, _S_default_co]:
        """Apply a synchronous function to the wrapped [trcks.Failure][] object.

        Wrapped [trcks.Success][] objects are passed on unchanged.

        Args:
            f: The synchronous function to be applied.

        Returns:
            A new [trcks.oop.AwaitableResultWrapper][] instance with

                - the result of the function application if
                    the original [trcks.AwaitableResult][] is a failure, or
                - the original [trcks.AwaitableResult][] object if it is a success.

        Example:
            >>> import asyncio
            >>> from trcks.oop import AwaitableResultWrapper
            >>> awaitable_result_wrapper_1 = (
            ...     AwaitableResultWrapper
            ...     .construct_failure("negative value")
            ...     .map_failure(lambda s: f"Prefix: {s}")
            ... )
            >>> awaitable_result_wrapper_1
            AwaitableResultWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_result_wrapper_1.core_as_coroutine)
            ('failure', 'Prefix: negative value')
            >>>
            >>> awaitable_result_wrapper_2 = (
            ...     AwaitableResultWrapper
            ...     .construct_success(25.0)
            ...     .map_failure(lambda s: f"Prefix: {s}")
            ... )
            >>> awaitable_result_wrapper_2
            AwaitableResultWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_result_wrapper_2.core_as_coroutine)
            ('success', 25.0)
        """
        return AwaitableResultWrapper(ar.map_failure(f)(self.core))

    def map_failure_to_awaitable(
        self, f: Callable[[_F_default_co], Awaitable[_F]]
    ) -> AwaitableResultWrapper[_F, _S_default_co]:
        """Apply an asynchronous function to the wrapped [trcks.Failure][] object.

        Wrapped [trcks.Success][] objects are passed on unchanged.

        Args:
            f: The asynchronous function to be applied.

        Returns:
            A new [trcks.oop.AwaitableResultWrapper][] instance with

                - the result of the function application if
                    the original [trcks.AwaitableResult][] is a failure, or
                - the original [trcks.AwaitableResult][] object if it is a success.

        Example:
            >>> import asyncio
            >>> from trcks.oop import AwaitableResultWrapper
            >>> async def add_prefix_slowly(s: str) -> str:
            ...     await asyncio.sleep(0.001)
            ...     return f"Prefix: {s}"
            ...
            >>> awaitable_result_wrapper_1 = (
            ...     AwaitableResultWrapper
            ...     .construct_failure("not found")
            ...     .map_failure_to_awaitable(add_prefix_slowly)
            ... )
            >>> awaitable_result_wrapper_1
            AwaitableResultWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_result_wrapper_1.core_as_coroutine)
            ('failure', 'Prefix: not found')
            >>>
            >>> awaitable_result_wrapper_2 = (
            ...     AwaitableResultWrapper
            ...     .construct_success(42)
            ...     .map_failure_to_awaitable(add_prefix_slowly)
            ... )
            >>> awaitable_result_wrapper_2
            AwaitableResultWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_result_wrapper_2.core_as_coroutine)
            ('success', 42)
        """
        return AwaitableResultWrapper(ar.map_failure_to_awaitable(f)(self.core))

    def map_failure_to_awaitable_result(
        self, f: Callable[[_F_default_co], AwaitableResult[_F, _S]]
    ) -> AwaitableResultWrapper[_F, _S_default_co | _S]:
        """Apply an asynchronous function with return type [trcks.Result][]
        to the wrapped [trcks.Failure][] object.

        Wrapped [trcks.Success][] objects are passed on unchanged.

        Args:
            f: The asynchronous function to be applied.

        Returns:
            A new [trcks.oop.AwaitableResultWrapper][] instance with

                - the result of the function application if
                    the original [trcks.AwaitableResult][] is a failure, or
                - the original [trcks.AwaitableResult][] object if it is a success.

        Example:
            >>> import asyncio
            >>> from trcks import Result
            >>> from trcks.oop import AwaitableResultWrapper
            >>> async def slowly_replace_not_found(s: str) -> Result[str, float]:
            ...     await asyncio.sleep(0.001)
            ...     if s == "not found":
            ...         return "success", 0.0
            ...     return "failure", s
            ...
            >>> awaitable_result_wrapper_1 = (
            ...     AwaitableResultWrapper
            ...     .construct_failure("not found")
            ...     .map_failure_to_awaitable_result(slowly_replace_not_found)
            ... )
            >>> awaitable_result_wrapper_1
            AwaitableResultWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_result_wrapper_1.core_as_coroutine)
            ('success', 0.0)
            >>>
            >>> awaitable_result_wrapper_2 = (
            ...     AwaitableResultWrapper
            ...     .construct_failure("other failure")
            ...     .map_failure_to_awaitable_result(slowly_replace_not_found)
            ... )
            >>> awaitable_result_wrapper_2
            AwaitableResultWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_result_wrapper_2.core_as_coroutine)
            ('failure', 'other failure')
            >>>
            >>> awaitable_result_wrapper_3 = (
            ...     AwaitableResultWrapper
            ...     .construct_success(25.0)
            ...     .map_failure_to_awaitable_result(slowly_replace_not_found)
            ... )
            >>> awaitable_result_wrapper_3
            AwaitableResultWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_result_wrapper_3.core_as_coroutine)
            ('success', 25.0)
        """
        return AwaitableResultWrapper(ar.map_failure_to_awaitable_result(f)(self.core))

    def map_failure_to_awaitable_result_tuple(
        self, f: Callable[[_F_default_co], AwaitableResultTuple[_F, _S]]
    ) -> AwaitableResultTupleWrapper[_F, _S_default_co | _S]:
        """Apply an asynchronous function with return type
        [trcks.ResultTuple][] to the wrapped [trcks.Failure][] object.

        Wrapped [trcks.Success][] objects are passed on unchanged.

        Args:
            f: The asynchronous function to be applied.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - the result of the function application if
                    the original [trcks.AwaitableResult][] is a failure, or
                - the original [trcks.AwaitableResult][] if it is a success.

        Example:
            >>> import asyncio
            >>> from trcks import AwaitableResultTuple
            >>> from trcks.oop import AwaitableResultWrapper
            >>> async def recover(
            ...     e: str,
            ... ) -> AwaitableResultTuple[str, float]:
            ...     await asyncio.sleep(0.001)
            ...     if e == "not found":
            ...         return "success", (0.0, 1.0)
            ...     return "failure", e
            ...
            >>> wrapper_1 = (
            ...     AwaitableResultWrapper
            ...     .construct_failure("not found")
            ...     .map_failure_to_awaitable_result_tuple(recover)
            ... )
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('success', (0.0, 1.0))
            >>>
            >>> wrapper_2 = (
            ...     AwaitableResultWrapper
            ...     .construct_success(25.0)
            ...     .map_failure_to_awaitable_result_tuple(recover)
            ... )
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('success', (25.0,))
        """
        return AwaitableResultTupleWrapper.construct_from_awaitable_result(
            self.core
        ).map_failure_to_awaitable_result_tuple(f)

    def map_failure_to_result(
        self, f: Callable[[_F_default_co], Result[_F, _S]]
    ) -> AwaitableResultWrapper[_F, _S_default_co | _S]:
        """Apply a synchronous function with return type [trcks.Result][]
        to the wrapped [trcks.Failure][] object.

        Wrapped [trcks.Success][] objects are passed on unchanged.

        Args:
            f: The synchronous function to be applied.

        Returns:
            A new [trcks.oop.AwaitableResultWrapper][] instance with

                - the result of the function application if
                    the original [trcks.AwaitableResult][] is a failure, or
                - the original [trcks.AwaitableResult][] object if it is a success.

        Example:
            >>> import asyncio
            >>> from trcks import Result
            >>> from trcks.oop import AwaitableResultWrapper
            >>> def replace_not_found_by_default_value(s: str) -> Result[str, float]:
            ...     if s == "not found":
            ...         return "success", 0.0
            ...     return "failure", s
            ...
            >>> awaitable_result_wrapper_1 = (
            ...     AwaitableResultWrapper
            ...     .construct_failure("not found")
            ...     .map_failure_to_result(replace_not_found_by_default_value)
            ... )
            >>> awaitable_result_wrapper_1
            AwaitableResultWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_result_wrapper_1.core_as_coroutine)
            ('success', 0.0)
            >>>
            >>> awaitable_result_wrapper_2 = (
            ...     AwaitableResultWrapper
            ...     .construct_failure("other failure")
            ...     .map_failure_to_result(replace_not_found_by_default_value)
            ... )
            >>> awaitable_result_wrapper_2
            AwaitableResultWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_result_wrapper_2.core_as_coroutine)
            ('failure', 'other failure')
            >>>
            >>> awaitable_result_wrapper_3 = (
            ...     AwaitableResultWrapper
            ...     .construct_success(25.0)
            ...     .map_failure_to_result(replace_not_found_by_default_value)
            ... )
            >>> awaitable_result_wrapper_3
            AwaitableResultWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_result_wrapper_3.core_as_coroutine)
            ('success', 25.0)
        """
        return AwaitableResultWrapper(ar.map_failure_to_result(f)(self.core))

    def map_failure_to_result_tuple(
        self, f: Callable[[_F_default_co], ResultTuple[_F, _S]]
    ) -> AwaitableResultTupleWrapper[_F, _S_default_co | _S]:
        """Apply a synchronous function with return type [trcks.ResultTuple][]
        to the wrapped [trcks.Failure][] object.

        Wrapped [trcks.Success][] objects are passed on unchanged.

        Args:
            f: The synchronous function to be applied.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - the result of the function application if
                    the original [trcks.AwaitableResult][] is a failure, or
                - the original [trcks.AwaitableResult][] if it is a success.

        Example:
            >>> import asyncio
            >>> from trcks import ResultTuple
            >>> from trcks.oop import AwaitableResultWrapper
            >>> def recover(e: str) -> ResultTuple[str, float]:
            ...     if e == "not found":
            ...         return "success", (0.0, 1.0)
            ...     return "failure", e
            ...
            >>> wrapper_1 = (
            ...     AwaitableResultWrapper
            ...     .construct_failure("not found")
            ...     .map_failure_to_result_tuple(recover)
            ... )
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('success', (0.0, 1.0))
            >>>
            >>> wrapper_2 = (
            ...     AwaitableResultWrapper
            ...     .construct_success(25.0)
            ...     .map_failure_to_result_tuple(recover)
            ... )
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('success', (25.0,))
        """
        return AwaitableResultTupleWrapper.construct_from_awaitable_result(
            self.core
        ).map_failure_to_result_tuple(f)

    def map_failure_to_tuple(
        self, f: Callable[[_F_default_co], tuple[_S, ...]]
    ) -> AwaitableResultTupleWrapper[Never, _S_default_co | _S]:
        """Apply a synchronous function returning a homogeneous [tuple][]
        to the wrapped [trcks.Failure][] object.

        The failure is converted to a [trcks.SuccessTuple][].
        Wrapped [trcks.Success][] objects are passed on unchanged.

        Args:
            f: The synchronous function to be applied,
                returning a homogeneous [tuple][].

        Returns:
            A [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - a [trcks.SuccessTuple][] containing the result of the
                    function application if
                    the original [trcks.AwaitableResult][] is a failure, or
                - the original [trcks.AwaitableResult][] if it is a success.

        Example:
            >>> import asyncio
            >>> from trcks.oop import AwaitableResultWrapper
            >>> def recover(e: str) -> tuple[float, ...]:
            ...     if e == "not found":
            ...         return (0.0, 1.0)
            ...     return ()
            ...
            >>> wrapper_1 = (
            ...     AwaitableResultWrapper
            ...     .construct_failure("not found")
            ...     .map_failure_to_tuple(recover)
            ... )
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('success', (0.0, 1.0))
            >>>
            >>> wrapper_2 = (
            ...     AwaitableResultWrapper
            ...     .construct_success(25.0)
            ...     .map_failure_to_tuple(recover)
            ... )
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('success', (25.0,))
        """
        return AwaitableResultTupleWrapper.construct_from_awaitable_result(
            self.core
        ).map_failure_to_tuple(f)

    def map_success(
        self, f: Callable[[_S_default_co], _S]
    ) -> AwaitableResultWrapper[_F_default_co, _S]:
        """Apply a synchronous function to the wrapped [trcks.Success][] object.

        Wrapped [trcks.Failure][] objects are passed on unchanged.

        Args:
            f: The synchronous function to be applied.

        Returns:
            A new [trcks.oop.AwaitableResultWrapper][] instance with

                - the original [trcks.AwaitableResult][] object if it is a failure, or
                - the result of the function application if
                    the original [trcks.AwaitableResult][] is a success.

        Example:
            >>> import asyncio
            >>> import math
            >>> from trcks.oop import AwaitableResultWrapper
            >>> awaitable_result_wrapper_1 = (
            ...     AwaitableResultWrapper
            ...     .construct_failure("not found")
            ...     .map_success(lambda n: n + 1)
            ... )
            >>> awaitable_result_wrapper_1
            AwaitableResultWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_result_wrapper_1.core_as_coroutine)
            ('failure', 'not found')
            >>>
            >>> awaitable_result_wrapper_2 = (
            ...     AwaitableResultWrapper
            ...     .construct_success(42)
            ...     .map_success(lambda n: n + 1)
            ... )
            >>> awaitable_result_wrapper_2
            AwaitableResultWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_result_wrapper_2.core_as_coroutine)
            ('success', 43)
        """
        return AwaitableResultWrapper(ar.map_success(f)(self.core))

    def map_success_to_awaitable(
        self, f: Callable[[_S_default_co], Awaitable[_S]]
    ) -> AwaitableResultWrapper[_F_default_co, _S]:
        """Apply an asynchronous function to the wrapped [trcks.Success][] object.

        Wrapped [trcks.Failure][] objects are passed on unchanged.

        Args:
            f: The asynchronous function to be applied.

        Returns:
            A new [trcks.oop.AwaitableResultWrapper][] instance with

                - the original [trcks.AwaitableResult][] object if it is a failure, or
                - the result of the function application if
                    the original [trcks.AwaitableResult][] is a success.

        Example:
            >>> import asyncio
            >>> from trcks.oop import AwaitableResultWrapper
            >>> async def increment_slowly(n: int) -> int:
            ...     await asyncio.sleep(0.001)
            ...     return n + 1
            ...
            >>> awaitable_result_wrapper_1 = (
            ...     AwaitableResultWrapper
            ...     .construct_failure("not found")
            ...     .map_success_to_awaitable(increment_slowly)
            ... )
            >>> awaitable_result_wrapper_1
            AwaitableResultWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_result_wrapper_1.core_as_coroutine)
            ('failure', 'not found')
            >>>
            >>> awaitable_result_wrapper_2 = (
            ...     AwaitableResultWrapper
            ...     .construct_success(42)
            ...     .map_success_to_awaitable(increment_slowly)
            ... )
            >>> awaitable_result_wrapper_2
            AwaitableResultWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_result_wrapper_2.core_as_coroutine)
            ('success', 43)
        """
        return AwaitableResultWrapper(ar.map_success_to_awaitable(f)(self.core))

    def map_success_to_awaitable_result(
        self, f: Callable[[_S_default_co], AwaitableResult[_F, _S]]
    ) -> AwaitableResultWrapper[_F_default_co | _F, _S]:
        """Apply an asynchronous function with return type [trcks.Result][]
        to the wrapped [trcks.Success][] object.

        Wrapped [trcks.Failure][] objects are passed on unchanged.

        Args:
            f: The asynchronous function to be applied.

        Returns:
            A new [trcks.oop.AwaitableResultWrapper][] instance with

                - the original [trcks.AwaitableResult][] object if it is a failure, or
                - the result of the function application if
                    the original [trcks.AwaitableResult][] is a success.

        Example:
            >>> import asyncio
            >>> import math
            >>> from trcks import Result
            >>> from trcks.oop import AwaitableResultWrapper
            >>> async def get_square_root_slowly(x: float) -> Result[str, float]:
            ...     await asyncio.sleep(0.001)
            ...     if x < 0:
            ...         return "failure", "negative value"
            ...     return "success", math.sqrt(x)
            ...
            >>> awaitable_result_wrapper_1 = (
            ...     AwaitableResultWrapper
            ...     .construct_failure("not found")
            ...     .map_success_to_awaitable_result(get_square_root_slowly)
            ... )
            >>> awaitable_result_wrapper_1
            AwaitableResultWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_result_wrapper_1.core_as_coroutine)
            ('failure', 'not found')
            >>>
            >>> awaitable_result_wrapper_2 = (
            ...     AwaitableResultWrapper
            ...     .construct_success(-25.0)
            ...     .map_success_to_awaitable_result(get_square_root_slowly)
            ... )
            >>> awaitable_result_wrapper_2
            AwaitableResultWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_result_wrapper_2.core_as_coroutine)
            ('failure', 'negative value')
            >>>
            >>> awaitable_result_wrapper_3 = (
            ...     AwaitableResultWrapper
            ...     .construct_success(25.0)
            ...     .map_success_to_awaitable_result(get_square_root_slowly)
            ... )
            >>> awaitable_result_wrapper_3
            AwaitableResultWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_result_wrapper_3.core_as_coroutine)
            ('success', 5.0)
        """
        return AwaitableResultWrapper(ar.map_success_to_awaitable_result(f)(self.core))

    def map_success_to_awaitable_result_tuple(
        self, f: Callable[[_S_default_co], AwaitableResultTuple[_F, _S]]
    ) -> AwaitableResultTupleWrapper[_F_default_co | _F, _S]:
        """Apply an asynchronous function with return type
        [trcks.ResultTuple][] to the wrapped [trcks.Success][] object.

        Wrapped [trcks.Failure][] objects are passed on unchanged.

        Args:
            f: The asynchronous function to be applied.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - the original [trcks.AwaitableResult][] if it is a failure, or
                - the result of the function application if
                    the original [trcks.AwaitableResult][] is a success.

        Example:
            >>> import asyncio
            >>> from trcks import AwaitableResultTuple
            >>> from trcks.oop import AwaitableResultWrapper
            >>> async def slowly_expand(
            ...     x: float,
            ... ) -> AwaitableResultTuple[str, float]:
            ...     await asyncio.sleep(0.001)
            ...     if x < 0:
            ...         return "failure", "negative"
            ...     return "success", (x, x * 2)
            ...
            >>> wrapper_1 = (
            ...     AwaitableResultWrapper
            ...     .construct_failure("not found")
            ...     .map_success_to_awaitable_result_tuple(slowly_expand)
            ... )
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('failure', 'not found')
            >>>
            >>> wrapper_2 = (
            ...     AwaitableResultWrapper
            ...     .construct_success(5.0)
            ...     .map_success_to_awaitable_result_tuple(slowly_expand)
            ... )
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('success', (5.0, 10.0))
        """
        return AwaitableResultTupleWrapper.construct_from_awaitable_result(
            self.core
        ).map_successes_to_awaitable_result_tuple(f)

    def map_success_to_result(
        self, f: Callable[[_S_default_co], Result[_F, _S]]
    ) -> AwaitableResultWrapper[_F_default_co | _F, _S]:
        """Apply a synchronous function with return type [trcks.Result][]
        to the wrapped [trcks.Success][] object.

        Wrapped [trcks.Failure][] objects are passed on unchanged.

        Args:
            f: The synchronous function to be applied.

        Returns:
            A new [trcks.oop.AwaitableResultWrapper][] instance with

                - the original [trcks.AwaitableResult][] object if it is a failure, or
                - the result of the function application if
                    the original [trcks.AwaitableResult][] is a success.

        Example:
            >>> import asyncio
            >>> import math
            >>> from trcks import Result
            >>> from trcks.oop import AwaitableResultWrapper
            >>> def get_square_root(x: float) -> Result[str, float]:
            ...     if x < 0:
            ...         return "failure", "negative value"
            ...     return "success", math.sqrt(x)
            ...
            >>> awaitable_result_1 = (
            ...     AwaitableResultWrapper
            ...     .construct_failure("not found")
            ...     .map_success_to_result(get_square_root)
            ... )
            >>> awaitable_result_1
            AwaitableResultWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_result_1.core_as_coroutine)
            ('failure', 'not found')
            >>>
            >>> awaitable_result_2 = (
            ...     AwaitableResultWrapper
            ...     .construct_success(-25.0)
            ...     .map_success_to_result(get_square_root)
            ... )
            >>> awaitable_result_2
            AwaitableResultWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_result_2.core_as_coroutine)
            ('failure', 'negative value')
            >>>
            >>> awaitable_result_3 = (
            ...     AwaitableResultWrapper
            ...     .construct_success(25.0)
            ...     .map_success_to_result(get_square_root)
            ... )
            >>> awaitable_result_3
            AwaitableResultWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_result_3.core_as_coroutine)
            ('success', 5.0)
        """
        return AwaitableResultWrapper(ar.map_success_to_result(f)(self.core))

    def map_success_to_result_tuple(
        self, f: Callable[[_S_default_co], ResultTuple[_F, _S]]
    ) -> AwaitableResultTupleWrapper[_F_default_co | _F, _S]:
        """Apply a synchronous function with return type [trcks.ResultTuple][]
        to the wrapped [trcks.Success][] object.

        Wrapped [trcks.Failure][] objects are passed on unchanged.

        Args:
            f: The synchronous function to be applied.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - the original [trcks.AwaitableResult][] if it is a failure, or
                - the result of the function application if
                    the original [trcks.AwaitableResult][] is a success.

        Example:
            >>> import asyncio
            >>> from trcks import ResultTuple
            >>> from trcks.oop import AwaitableResultWrapper
            >>> def expand(x: float) -> ResultTuple[str, float]:
            ...     if x < 0:
            ...         return "failure", "negative"
            ...     return "success", (x, x * 2)
            ...
            >>> wrapper_1 = (
            ...     AwaitableResultWrapper
            ...     .construct_failure("not found")
            ...     .map_success_to_result_tuple(expand)
            ... )
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('failure', 'not found')
            >>>
            >>> wrapper_2 = (
            ...     AwaitableResultWrapper
            ...     .construct_success(5.0)
            ...     .map_success_to_result_tuple(expand)
            ... )
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('success', (5.0, 10.0))
        """
        return AwaitableResultTupleWrapper.construct_from_awaitable_result(
            self.core
        ).map_successes_to_result_tuple(f)

    def map_success_to_tuple(
        self, f: Callable[[_S_default_co], tuple[_S, ...]]
    ) -> AwaitableResultTupleWrapper[_F_default_co, _S]:
        """Apply a synchronous function returning a homogeneous [tuple][]
        to the wrapped [trcks.Success][] object.

        Wrapped [trcks.Failure][] objects are passed on unchanged.

        Args:
            f: The synchronous function to be applied,
                returning a homogeneous [tuple][].

        Returns:
            A [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - the original [trcks.AwaitableResult][] if it is a failure, or
                - an awaitable [trcks.SuccessTuple][] containing the result
                    of the function application if
                    the original [trcks.AwaitableResult][] is a success.

        Example:
            >>> import asyncio
            >>> from trcks.oop import AwaitableResultWrapper
            >>> def duplicate(x: float) -> tuple[float, ...]:
            ...     return (x, x)
            ...
            >>> wrapper_1 = (
            ...     AwaitableResultWrapper
            ...     .construct_failure("not found")
            ...     .map_success_to_tuple(duplicate)
            ... )
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('failure', 'not found')
            >>>
            >>> wrapper_2 = (
            ...     AwaitableResultWrapper
            ...     .construct_success(5.0)
            ...     .map_success_to_tuple(duplicate)
            ... )
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('success', (5.0, 5.0))
        """
        return AwaitableResultTupleWrapper.construct_from_awaitable_result(
            self.core
        ).map_successes_to_tuple(f)

    def tap_failure(
        self, f: Callable[[_F_default_co], object]
    ) -> AwaitableResultWrapper[_F_default_co, _S_default_co]:
        """Apply a synchronous side effect to the wrapped [trcks.Failure][] object.

        Wrapped [trcks.Success][] objects are passed on without side effects.

        Args:
            f: The synchronous side effect to be applied.

        Returns:
            A new [trcks.oop.AwaitableResultWrapper][] instance
                with the original [trcks.Result][] object,
                allowing for further method chaining.

        Example:
            >>> import asyncio
            >>> from trcks.oop import AwaitableResultWrapper
            >>> awaitable_result_wrapper_1 = AwaitableResultWrapper.construct_failure(
            ...     "not found"
            ... ).tap_failure(lambda f: print(f"Failure: {f}"))
            >>> awaitable_result_wrapper_1
            AwaitableResultWrapper(core=<coroutine object ...>)
            >>> result_1 = asyncio.run(awaitable_result_wrapper_1.core_as_coroutine)
            Failure: not found
            >>> result_1
            ('failure', 'not found')
            >>> awaitable_result_wrapper_2 = AwaitableResultWrapper.construct_success(
            ...     42
            ... ).tap_failure(lambda f: print(f"Failure: {f}"))
            >>> awaitable_result_wrapper_2
            AwaitableResultWrapper(core=<coroutine object ...>)
            >>> result_2 = asyncio.run(awaitable_result_wrapper_2.core_as_coroutine)
            >>> result_2
            ('success', 42)
        """
        return AwaitableResultWrapper(ar.tap_failure(f)(self.core))

    def tap_failure_to_awaitable(
        self, f: Callable[[_F_default_co], Awaitable[object]]
    ) -> AwaitableResultWrapper[_F_default_co, _S_default_co]:
        """Apply an asynchronous side effect to the wrapped [trcks.Failure][] object.

        Wrapped [trcks.Success][] objects are passed on without side effects.

        Args:
            f: The asynchronous side effect to be applied.

        Returns:
            A new [trcks.oop.AwaitableResultWrapper][] instance
                with the original [trcks.Result][] object,
                allowing for further method chaining.

        Example:
            >>> import asyncio
            >>> from trcks.oop import AwaitableResultWrapper
            >>> async def write_to_disk(output: str) -> None:
            ...     await asyncio.sleep(0.001)
            ...     print(f"Wrote '{output}' to disk.")
            ...
            >>> awaitable_result_wrapper_1 = AwaitableResultWrapper.construct_failure(
            ...     "not found"
            ... ).tap_failure_to_awaitable(write_to_disk)
            >>> awaitable_result_wrapper_1
            AwaitableResultWrapper(core=<coroutine object ...>)
            >>> result_1 = asyncio.run(awaitable_result_wrapper_1.core_as_coroutine)
            Wrote 'not found' to disk.
            >>> result_1
            ('failure', 'not found')
            >>> awaitable_result_wrapper_2 = AwaitableResultWrapper.construct_success(
            ...     42
            ... ).tap_failure_to_awaitable(write_to_disk)
            >>> awaitable_result_wrapper_2
            AwaitableResultWrapper(core=<coroutine object ...>)
            >>> result_2 = asyncio.run(awaitable_result_wrapper_2.core_as_coroutine)
            >>> result_2
            ('success', 42)
        """
        return AwaitableResultWrapper(ar.tap_failure_to_awaitable(f)(self.core))

    def tap_failure_to_awaitable_result(
        self, f: Callable[[_F_default_co], AwaitableResult[object, _S]]
    ) -> AwaitableResultWrapper[_F_default_co, _S_default_co | _S]:
        """Apply an asynchronous side effect with return type [trcks.Result][]
        to the wrapped [trcks.Failure][] object.

        Wrapped [trcks.Success][] objects are passed on without side effects.

        Args:
            f: The asynchronous side effect to be applied.

        Returns:
            A new [trcks.oop.AwaitableResultWrapper][] instance with

                - *the original* [trcks.Failure][]
                    if the applied side effect returns a [trcks.Failure][],
                - *the returned* [trcks.Success][]
                    if the applied side effect returns a [trcks.Success][] and
                - *the original* [trcks.Success][] if no side effect was applied.
        """
        return AwaitableResultWrapper(ar.tap_failure_to_awaitable_result(f)(self.core))

    def tap_failure_to_awaitable_result_tuple(
        self, f: Callable[[_F_default_co], AwaitableResultTuple[object, _S]]
    ) -> AwaitableResultTupleWrapper[_F_default_co, _S_default_co | _S]:
        """Apply an asynchronous side effect with return type
        [trcks.ResultTuple][] to the wrapped [trcks.Failure][] object.

        Wrapped [trcks.Success][] objects are passed on without side effects.

        Args:
            f: The asynchronous side effect to be applied.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - *the original* [trcks.Failure][]
                    if the applied side effect returns a [trcks.Failure][],
                - *the returned* [trcks.SuccessTuple][]
                    if the applied side effect returns a [trcks.SuccessTuple][]
                    and
                - *the original* [trcks.Success][] if no side effect was applied.

        Example:
            >>> import asyncio
            >>> from trcks import AwaitableResultTuple
            >>> from trcks.oop import AwaitableResultWrapper
            >>> async def recover(
            ...     e: str,
            ... ) -> AwaitableResultTuple[object, float]:
            ...     await asyncio.sleep(0.001)
            ...     if e == "not found":
            ...         return "success", (0.0, 1.0)
            ...     return "failure", e
            ...
            >>> wrapper_1 = (
            ...     AwaitableResultWrapper
            ...     .construct_failure("not found")
            ...     .tap_failure_to_awaitable_result_tuple(recover)
            ... )
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('success', (0.0, 1.0))
            >>>
            >>> wrapper_2 = (
            ...     AwaitableResultWrapper
            ...     .construct_success(42)
            ...     .tap_failure_to_awaitable_result_tuple(recover)
            ... )
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('success', (42,))
        """
        return AwaitableResultTupleWrapper.construct_from_awaitable_result(
            self.core
        ).tap_failure_to_awaitable_result_tuple(f)

    def tap_failure_to_result(
        self, f: Callable[[_F_default_co], Result[object, _S]]
    ) -> AwaitableResultWrapper[_F_default_co, _S_default_co | _S]:
        """Apply a synchronous side effect with return type [trcks.Result][]
        to the wrapped [trcks.Failure][] object.

        Wrapped [trcks.Success][] objects are passed on without side effects.

        Args:
            f: The synchronous side effect to be applied.

        Returns:
            A new [trcks.oop.AwaitableResultWrapper][] instance with

                - *the original* [trcks.Failure][]
                    if the applied side effect returns a [trcks.Failure][],
                - *the returned* [trcks.Success][]
                    if the applied side effect returns a [trcks.Success][] and
                - *the original* [trcks.Success][] if no side effect was applied.

        Example:
            >>> import asyncio
            >>> from trcks import Result
            >>> from trcks.oop import AwaitableResultWrapper
            >>> def replace_not_found_with_default(s: str) -> Result[object, float]:
            ...     if s == "not found":
            ...         return "success", 0.0
            ...     return "failure", s
            ...
            >>> awaitable_result_wrapper_1 = (
            ...     AwaitableResultWrapper
            ...     .construct_failure("not found")
            ...     .tap_failure_to_result(replace_not_found_with_default)
            ... )
            >>> awaitable_result_wrapper_1
            AwaitableResultWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_result_wrapper_1.core_as_coroutine)
            ('success', 0.0)
            >>>
            >>> awaitable_result_wrapper_2 = (
            ...     AwaitableResultWrapper
            ...     .construct_failure("other error")
            ...     .tap_failure_to_result(replace_not_found_with_default)
            ... )
            >>> awaitable_result_wrapper_2
            AwaitableResultWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_result_wrapper_2.core_as_coroutine)
            ('failure', 'other error')
            >>>
            >>> awaitable_result_wrapper_3 = (
            ...     AwaitableResultWrapper
            ...     .construct_success(42)
            ...     .tap_failure_to_result(replace_not_found_with_default)
            ... )
            >>> awaitable_result_wrapper_3
            AwaitableResultWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_result_wrapper_3.core_as_coroutine)
            ('success', 42)
        """
        return AwaitableResultWrapper(ar.tap_failure_to_result(f)(self.core))

    def tap_failure_to_result_tuple(
        self, f: Callable[[_F_default_co], ResultTuple[object, _S]]
    ) -> AwaitableResultTupleWrapper[_F_default_co, _S_default_co | _S]:
        """Apply a synchronous side effect with return type [trcks.ResultTuple][]
        to the wrapped [trcks.Failure][] object.

        Wrapped [trcks.Success][] objects are passed on without side effects.

        Args:
            f: The synchronous side effect to be applied.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - *the original* [trcks.Failure][]
                    if the applied side effect returns a [trcks.Failure][],
                - *the returned* [trcks.SuccessTuple][]
                    if the applied side effect returns a [trcks.SuccessTuple][]
                    and
                - *the original* [trcks.Success][] if no side effect was applied.

        Example:
            >>> import asyncio
            >>> from trcks import ResultTuple
            >>> from trcks.oop import AwaitableResultWrapper
            >>> def recover(e: str) -> ResultTuple[object, float]:
            ...     if e == "not found":
            ...         return "success", (0.0, 1.0)
            ...     return "failure", e
            ...
            >>> wrapper_1 = (
            ...     AwaitableResultWrapper
            ...     .construct_failure("not found")
            ...     .tap_failure_to_result_tuple(recover)
            ... )
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('success', (0.0, 1.0))
            >>>
            >>> wrapper_2 = (
            ...     AwaitableResultWrapper
            ...     .construct_success(42)
            ...     .tap_failure_to_result_tuple(recover)
            ... )
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('success', (42,))
        """
        return AwaitableResultTupleWrapper.construct_from_awaitable_result(
            self.core
        ).tap_failure_to_result_tuple(f)

    def tap_failure_to_tuple(
        self, f: Callable[[_F_default_co], tuple[object, ...]]
    ) -> AwaitableResultTupleWrapper[Never, _F_default_co | _S_default_co]:
        """Apply a synchronous side effect returning a [tuple][]
        to the wrapped [trcks.Failure][] object.

        The failure is converted to a [trcks.SuccessTuple][] where
        the original failure value is repeated once per element in
        the tuple returned by the side effect.

        Wrapped [trcks.Success][] objects are passed on without side effects.

        Args:
            f: The synchronous side effect to be applied.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - a [trcks.SuccessTuple][] containing the original failure
                    repeated once per element returned by the side effect
                    if the original [trcks.AwaitableResult][] is a failure, or
                - the original [trcks.AwaitableResult][] if it is a success.

        Example:
            >>> import asyncio
            >>> from trcks.oop import AwaitableResultWrapper
            >>> def log_err(e: str) -> tuple[None, ...]:
            ...     print(f"Error logged: {e}")
            ...     print(f"Alert sent: {e}")
            ...     return (None, None)
            ...
            >>> wrapper_1 = (
            ...     AwaitableResultWrapper
            ...     .construct_failure("critical")
            ...     .tap_failure_to_tuple(log_err)
            ... )
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> result_1 = asyncio.run(wrapper_1.core_as_coroutine)
            Error logged: critical
            Alert sent: critical
            >>> result_1
            ('success', ('critical', 'critical'))
            >>>
            >>> wrapper_2 = (
            ...     AwaitableResultWrapper
            ...     .construct_success(42)
            ...     .tap_failure_to_tuple(log_err)
            ... )
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('success', (42,))
        """
        return AwaitableResultTupleWrapper.construct_from_awaitable_result(
            self.core
        ).tap_failure_to_tuple(f)

    def tap_success(
        self, f: Callable[[_S_default_co], object]
    ) -> AwaitableResultWrapper[_F_default_co, _S_default_co]:
        """Apply a synchronous side effect to the wrapped [trcks.Success][] object.

        Wrapped [trcks.Failure][] objects are passed on without side effects.

        Args:
            f: The synchronous side effect to be applied.

        Returns:
            A new [trcks.oop.AwaitableResultWrapper][] instance
                with the original [trcks.Result][] object,
                allowing for further method chaining.

        Example:
            >>> import asyncio
            >>> from trcks.oop import AwaitableResultWrapper
            >>> awaitable_result_wrapper_1 = AwaitableResultWrapper.construct_failure(
            ...     "not found"
            ... ).tap_success(lambda n: print(f"Number: {n}"))
            >>> awaitable_result_wrapper_1
            AwaitableResultWrapper(core=<coroutine object ...>)
            >>> result_1 = asyncio.run(awaitable_result_wrapper_1.core_as_coroutine)
            >>> result_1
            ('failure', 'not found')
            >>> awaitable_result_wrapper_2 = AwaitableResultWrapper.construct_success(
            ...     42
            ... ).tap_success(lambda n: print(f"Number: {n}"))
            >>> awaitable_result_wrapper_2
            AwaitableResultWrapper(core=<coroutine object ...>)
            >>> result_2 = asyncio.run(awaitable_result_wrapper_2.core_as_coroutine)
            Number: 42
            >>> result_2
            ('success', 42)
        """
        return AwaitableResultWrapper(ar.tap_success(f)(self.core))

    def tap_success_to_awaitable(
        self, f: Callable[[_S_default_co], Awaitable[object]]
    ) -> AwaitableResultWrapper[_F_default_co, _S_default_co]:
        """Apply an asynchronous side effect to the wrapped [trcks.Success][] object.

        Wrapped [trcks.Failure][] objects are passed on without side effects.

        Args:
            f: The asynchronous side effect to be applied.

        Returns:
            A new [trcks.oop.AwaitableResultWrapper][] instance
                with the original [trcks.Result][] object,
                allowing for further method chaining.

        Example:
            >>> import asyncio
            >>> from trcks.oop import AwaitableResultWrapper
            >>> async def write_to_disk(output: str) -> None:
            ...     await asyncio.sleep(0.001)
            ...     print(f"Wrote '{output}' to disk.")
            ...
            >>> awaitable_result_wrapper_1 = AwaitableResultWrapper.construct_failure(
            ...     "not found"
            ... ).tap_success_to_awaitable(write_to_disk)
            >>> awaitable_result_wrapper_1
            AwaitableResultWrapper(core=<coroutine object ...>)
            >>> result_1 = asyncio.run(awaitable_result_wrapper_1.core_as_coroutine)
            >>> result_1
            ('failure', 'not found')
            >>> awaitable_result_wrapper_2 = AwaitableResultWrapper.construct_success(
            ...     "Hello, world!"
            ... ).tap_success_to_awaitable(write_to_disk)
            >>> awaitable_result_wrapper_2
            AwaitableResultWrapper(core=<coroutine object ...>)
            >>> result_2 = asyncio.run(awaitable_result_wrapper_2.core_as_coroutine)
            Wrote 'Hello, world!' to disk.
            >>> result_2
            ('success', 'Hello, world!')
        """
        return AwaitableResultWrapper(ar.tap_success_to_awaitable(f)(self.core))

    def tap_success_to_awaitable_result(
        self, f: Callable[[_S_default_co], AwaitableResult[_F, object]]
    ) -> AwaitableResultWrapper[_F_default_co | _F, _S_default_co]:
        """Apply an asynchronous side effect with return type [trcks.Result][]
        to the wrapped [trcks.Success][] object.

        Wrapped [trcks.Failure][] objects are passed on without side effects.

        Args:
            f: The asynchronous side effect to be applied.

        Returns:
            A new [trcks.oop.AwaitableResultWrapper][] instance with

                - *the original* [trcks.Failure][] if no side effect was applied,
                - *the returned* [trcks.Failure][]
                    if the applied side effect returns a [trcks.Failure][] and
                - *the original* [trcks.Success][]
                    if the applied side effect returns a [trcks.Success][].

        Example:
            >>> import asyncio
            >>> from trcks import Result
            >>> from trcks.oop import AwaitableResultWrapper
            >>> async def write_to_disk(s: str, path: str) -> Result[str, None]:
            ...     if path != "output.txt":
            ...         return "failure", "write error"
            ...     await asyncio.sleep(0.001)
            ...     print(f"Wrote '{s}' to file {path}.")
            ...     return "success", None
            ...
            >>> awaitable_result_wrapper_1 = AwaitableResultWrapper.construct_failure(
            ...     "missing text"
            ... ).tap_success_to_awaitable_result(
            ...     lambda s: write_to_disk(s, "destination.txt")
            ... )
            >>> awaitable_result_wrapper_1
            AwaitableResultWrapper(core=<coroutine object ...>)
            >>> result_1 = asyncio.run(awaitable_result_wrapper_1.core_as_coroutine)
            >>> result_1
            ('failure', 'missing text')
            >>> awaitable_result_wrapper_2 = AwaitableResultWrapper.construct_failure(
            ...     "missing text"
            ... ).tap_success_to_awaitable_result(
            ...     lambda s: write_to_disk(s, "output.txt")
            ... )
            >>> awaitable_result_wrapper_2
            AwaitableResultWrapper(core=<coroutine object ...>)
            >>> result_2 = asyncio.run(awaitable_result_wrapper_2.core_as_coroutine)
            >>> result_2
            ('failure', 'missing text')
            >>> awaitable_result_wrapper_3 = AwaitableResultWrapper.construct_success(
            ...     "Hello, world!"
            ... ).tap_success_to_awaitable_result(
            ...     lambda s: write_to_disk(s, "destination.txt")
            ... )
            >>> awaitable_result_wrapper_3
            AwaitableResultWrapper(core=<coroutine object ...>)
            >>> result_3 = asyncio.run(awaitable_result_wrapper_3.core_as_coroutine)
            >>> result_3
            ('failure', 'write error')
            >>> awaitable_result_wrapper_4 = AwaitableResultWrapper.construct_success(
            ...     "Hello, world!"
            ... ).tap_success_to_awaitable_result(
            ...     lambda s: write_to_disk(s, "output.txt")
            ... )
            >>> awaitable_result_wrapper_4
            AwaitableResultWrapper(core=<coroutine object ...>)
            >>> result_4 = asyncio.run(awaitable_result_wrapper_4.core_as_coroutine)
            Wrote 'Hello, world!' to file output.txt.
            >>> result_4
            ('success', 'Hello, world!')
        """
        return AwaitableResultWrapper(ar.tap_success_to_awaitable_result(f)(self.core))

    def tap_success_to_awaitable_result_tuple(
        self, f: Callable[[_S_default_co], AwaitableResultTuple[_F, object]]
    ) -> AwaitableResultTupleWrapper[_F_default_co | _F, _S_default_co]:
        """Apply an asynchronous side effect with return type
        [trcks.ResultTuple][] to the wrapped [trcks.Success][] object.

        Wrapped [trcks.Failure][] objects are passed on without side effects.

        Args:
            f: The asynchronous side effect to be applied.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - *the original* [trcks.Failure][] if no side effect was applied,
                - *the returned* [trcks.Failure][]
                    if the applied side effect returns a [trcks.Failure][] and
                - *the original* [trcks.Success][] repeated once per element
                    in the returned [trcks.SuccessTuple][]
                    if the applied side effect returns a [trcks.SuccessTuple][].

        Example:
            >>> import asyncio
            >>> from trcks import AwaitableResultTuple
            >>> from trcks.oop import AwaitableResultWrapper
            >>> async def write_twice(
            ...     s: str,
            ... ) -> AwaitableResultTuple[str, None]:
            ...     await asyncio.sleep(0.001)
            ...     print(f"Wrote '{s}' twice.")
            ...     return "success", (None, None)
            ...
            >>> wrapper_1 = (
            ...     AwaitableResultWrapper
            ...     .construct_failure("missing text")
            ...     .tap_success_to_awaitable_result_tuple(write_twice)
            ... )
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('failure', 'missing text')
            >>>
            >>> wrapper_2 = (
            ...     AwaitableResultWrapper
            ...     .construct_success("Hello, world!")
            ...     .tap_success_to_awaitable_result_tuple(write_twice)
            ... )
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> result_2 = asyncio.run(wrapper_2.core_as_coroutine)
            Wrote 'Hello, world!' twice.
            >>> result_2
            ('success', ('Hello, world!', 'Hello, world!'))
        """
        return AwaitableResultTupleWrapper.construct_from_awaitable_result(
            self.core
        ).tap_successes_to_awaitable_result_tuple(f)

    def tap_success_to_result(
        self, f: Callable[[_S_default_co], Result[_F, object]]
    ) -> AwaitableResultWrapper[_F_default_co | _F, _S_default_co]:
        """Apply a synchronous side effect with return type [trcks.Result][]
        to the wrapped [trcks.Success][] object.

        Wrapped [trcks.Failure][] objects are passed on without side effects.

        Args:
            f: The synchronous side effect to be applied.

        Returns:
            A new [trcks.oop.AwaitableResultWrapper][] instance with

                - *the original* [trcks.Failure][] if no side effect was applied,
                - *the returned* [trcks.Failure][]
                    if the applied side effect returns a [trcks.Failure][] and
                - *the original* [trcks.Success][]
                    if the applied side effect returns a [trcks.Success][].
        """
        return AwaitableResultWrapper(ar.tap_success_to_result(f)(self.core))

    def tap_success_to_result_tuple(
        self, f: Callable[[_S_default_co], ResultTuple[_F, object]]
    ) -> AwaitableResultTupleWrapper[_F_default_co | _F, _S_default_co]:
        """Apply a synchronous side effect with return type [trcks.ResultTuple][]
        to the wrapped [trcks.Success][] object.

        Wrapped [trcks.Failure][] objects are passed on without side effects.

        Args:
            f: The synchronous side effect to be applied.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - *the original* [trcks.Failure][] if no side effect was applied,
                - *the returned* [trcks.Failure][]
                    if the applied side effect returns a [trcks.Failure][] and
                - *the original* [trcks.Success][] repeated once per element
                    in the returned [trcks.SuccessTuple][]
                    if the applied side effect returns a [trcks.SuccessTuple][].

        Example:
            >>> import asyncio
            >>> from trcks import ResultTuple
            >>> from trcks.oop import AwaitableResultWrapper
            >>> def audit(s: str) -> ResultTuple[str, None]:
            ...     if s:
            ...         return "success", (None, None)
            ...     return "failure", "empty"
            ...
            >>> wrapper_1 = (
            ...     AwaitableResultWrapper
            ...     .construct_failure("missing")
            ...     .tap_success_to_result_tuple(audit)
            ... )
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('failure', 'missing')
            >>>
            >>> wrapper_2 = (
            ...     AwaitableResultWrapper
            ...     .construct_success("Hello, world!")
            ...     .tap_success_to_result_tuple(audit)
            ... )
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('success', ('Hello, world!', 'Hello, world!'))
        """
        return AwaitableResultTupleWrapper.construct_from_awaitable_result(
            self.core
        ).tap_successes_to_result_tuple(f)

    def tap_success_to_tuple(
        self, f: Callable[[_S_default_co], tuple[object, ...]]
    ) -> AwaitableResultTupleWrapper[_F_default_co, _S_default_co]:
        """Apply a synchronous side effect returning a [tuple][]
        to the wrapped [trcks.Success][] object.

        The original success value is repeated once per element
        in the tuple returned by the side effect.

        Wrapped [trcks.Failure][] objects are passed on without side effects.

        Args:
            f: The synchronous side effect to be applied,
                returning a homogeneous [tuple][].

        Returns:
            A [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - *the original* [trcks.Failure][] if no side effect was applied, or
                - an awaitable [trcks.SuccessTuple][] where the original element
                    is repeated once per element in the tuple returned by the
                    side effect.

        Example:
            >>> import asyncio
            >>> from trcks.oop import AwaitableResultWrapper
            >>> def log_mult(n: int) -> tuple[None, ...]:
            ...     print(f"v={n}")
            ...     print(f"v={n}")
            ...     return (None, None)
            ...
            >>> wrapper_1 = (
            ...     AwaitableResultWrapper
            ...     .construct_failure("error")
            ...     .tap_success_to_tuple(log_mult)
            ... )
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('failure', 'error')
            >>>
            >>> wrapper_2 = (
            ...     AwaitableResultWrapper
            ...     .construct_success(7)
            ...     .tap_success_to_tuple(log_mult)
            ... )
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> result_2 = asyncio.run(wrapper_2.core_as_coroutine)
            v=7
            v=7
            >>> result_2
            ('success', (7, 7))
        """
        return AwaitableResultTupleWrapper.construct_from_awaitable_result(
            self.core
        ).tap_successes_to_tuple(f)


class AwaitableTupleWrapper(_AwaitableWrapper[tuple[_T_co, ...]]):
    """Type-safe and immutable wrapper for [trcks.AwaitableTuple][] objects.

    The wrapped object can be accessed
    via the attribute `trcks.oop.AwaitableTupleWrapper.core`.
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
        ...         .construct_from_tuple((1, 2, 3))
        ...         .map_to_awaitable(slowly_double)
        ...         .core
        ...     )
        ...
        >>> asyncio.run(main())
        (2, 4, 6)
    """

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
    def construct_from_tuple(
        tpl: tuple[_T, ...],
    ) -> AwaitableTupleWrapper[_T]:
        """Construct and wrap a [trcks.AwaitableTuple][] from a tuple.

        Args:
            tpl: The tuple to be wrapped.

        Returns:
            A new [trcks.oop.AwaitableTupleWrapper][] instance with
                the wrapped [trcks.AwaitableTuple][] object.

        Example:
            >>> import asyncio
            >>> from trcks.oop import AwaitableTupleWrapper
            >>> awaitable_tuple_wrapper = (
            ...     AwaitableTupleWrapper
            ...     .construct_from_tuple((1, 2))
            ... )
            >>> awaitable_tuple_wrapper
            AwaitableTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_tuple_wrapper.core_as_coroutine)
            (1, 2)
        """
        return AwaitableTupleWrapper(at.construct_from_tuple(tpl))

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
            ...     .construct_from_tuple((1, 2, 3))
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
            ...     .construct_from_tuple((1, 2))
            ...     .map_to_awaitable(slowly_add_one)
            ... )
            >>> awaitable_tuple_wrapper
            AwaitableTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_tuple_wrapper.core_as_coroutine)
            (2, 3)
        """
        return AwaitableTupleWrapper(at.map_to_awaitable(f)(self.core))

    def map_to_awaitable_tuple(
        self, f: Callable[[_T_co], AwaitableTuple[_T]]
    ) -> AwaitableTupleWrapper[_T]:
        """Apply an asynchronous function returning a homogeneous [tuple][]
        to each element in the wrapped [trcks.AwaitableTuple][] and flatten.

        Args:
            f: The asynchronous function to be applied to each element,
                returning a [trcks.AwaitableTuple][].

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
            ...     .construct_from_tuple((1, 2))
            ...     .map_to_awaitable_tuple(slowly_duplicate)
            ... )
            >>> awaitable_tuple_wrapper
            AwaitableTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_tuple_wrapper.core_as_coroutine)
            (1, 1, 2, 2)
        """
        return AwaitableTupleWrapper(at.map_to_awaitable_tuple(f)(self.core))

    def map_to_tuple(
        self, f: Callable[[_T_co], tuple[_T, ...]]
    ) -> AwaitableTupleWrapper[_T]:
        """Apply a synchronous function returning a tuple to each element in
        the wrapped [trcks.AwaitableTuple][] object and flatten.

        Args:
            f: The synchronous function to be applied to each element,
                returning a tuple.

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
            ...     .construct_from_tuple((1, 2))
            ...     .map_to_tuple(add_negative)
            ... )
            >>> awaitable_tuple_wrapper
            AwaitableTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_tuple_wrapper.core_as_coroutine)
            (1, -1, 2, -2)
        """
        return AwaitableTupleWrapper(at.map_to_tuple(f)(self.core))

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
            ...     .construct_from_tuple((1, 2))
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
            ...     .construct_from_tuple((1, 2))
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

    def tap_to_awaitable_tuple(
        self, f: Callable[[_T_co], AwaitableTuple[object]]
    ) -> AwaitableTupleWrapper[_T_co]:
        """Apply an asynchronous side effect returning a [trcks.AwaitableTuple][]
        to each element in the wrapped [trcks.AwaitableTuple][] object.

        Args:
            f: The asynchronous side effect to be applied to each element,
                returning a [trcks.AwaitableTuple][].

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
            ...     .construct_from_tuple((1, 2, 3, 4))
            ...     .tap_to_awaitable_tuple(slowly_get_divisors)
            ... )
            >>> awaitable_tuple_wrapper
            AwaitableTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_tuple_wrapper.core_as_coroutine)
            (1, 2, 2, 3, 3, 4, 4, 4)
        """
        return AwaitableTupleWrapper(at.tap_to_awaitable_tuple(f)(self.core))

    def tap_to_tuple(
        self, f: Callable[[_T_co], tuple[object, ...]]
    ) -> AwaitableTupleWrapper[_T_co]:
        """Apply a synchronous side effect returning a tuple to each element in
        the wrapped [trcks.AwaitableTuple][] object.

        Args:
            f: The synchronous side effect to be applied to each element,
                returning a tuple.

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
            ...     .construct_from_tuple((1, 2, 3, 4))
            ...     .tap_to_tuple(get_divisors)
            ... )
            >>> awaitable_tuple_wrapper
            AwaitableTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_tuple_wrapper.core_as_coroutine)
            (1, 2, 2, 3, 3, 4, 4, 4)
        """
        return AwaitableTupleWrapper(at.tap_to_tuple(f)(self.core))


class AwaitableWrapper(_AwaitableWrapper[_T_co]):
    """Type-safe and immutable wrapper for [collections.abc.Awaitable][] objects.

    The wrapped [collections.abc.Awaitable][] can be accessed
    via the attribute `trcks.oop.AwaitableWrapper.core`.
    The `trcks.oop.AwaitableWrapper.map*` methods allow method chaining.
    The `trcks.oop.AwaitableWrapper.tap*` methods allow for side effects
    without changing the wrapped object.

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
        >>> async def write_to_disk(s: str) -> None:
        ...     await asyncio.sleep(0.001)
        ...     print(f"Wrote '{s}' to disk.")
        ...
        >>> async def main() -> str:
        ...     awaitable_str = read_from_disk()
        ...     return await (
        ...         AwaitableWrapper
        ...         .construct_from_awaitable(awaitable_str)
        ...         .map(transform)
        ...         .tap_to_awaitable(write_to_disk)
        ...         .core
        ...     )
        ...
        >>> output = asyncio.run(main())
        Read 'Hello, world!' from disk.
        Wrote 'Length: 13' to disk.
        >>> output
        'Length: 13'
    """

    @staticmethod
    def construct(value: _T) -> AwaitableWrapper[_T]:
        """Construct and wrap an [collections.abc.Awaitable][] object from a value.

        Args:
            value: The value to be wrapped.

        Returns:
            A new [trcks.oop.AwaitableWrapper][] instance
                with the wrapped [collections.abc.Awaitable][] object.

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
            awtbl: The [collections.abc.Awaitable][] to be wrapped.

        Returns:
            A new [trcks.oop.AwaitableWrapper][] instance
                with the wrapped [collections.abc.Awaitable][] object.

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
        """Apply a synchronous function
        to the wrapped [collections.abc.Awaitable][] object.

        Args:
            f: The synchronous function to be applied.

        Returns:
            A new [trcks.oop.AwaitableWrapper][] instance with
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
        return AwaitableWrapper(a.map_(f)(self.core))

    def map_to_awaitable(
        self, f: Callable[[_T_co], Awaitable[_T]]
    ) -> AwaitableWrapper[_T]:
        """Apply an asynchronous function
        to the wrapped [collections.abc.Awaitable][] object.

        Args:
            f: The asynchronous function to be applied.

        Returns:
            A new [trcks.oop.AwaitableWrapper][] instance with
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
        return AwaitableWrapper(a.map_to_awaitable(f)(self.core))

    def map_to_awaitable_result(
        self, f: Callable[[_T_co], AwaitableResult[_F, _S]]
    ) -> AwaitableResultWrapper[_F, _S]:
        """Apply an asynchronous function with return type [trcks.Result][]
        to the wrapped [collections.abc.Awaitable][] object.

        Args:
            f: The asynchronous function to be applied.

        Returns:
            A [trcks.oop.AwaitableResultWrapper][] instance with
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
            ...         return "failure", "negative value"
            ...     return "success", x
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

    def map_to_awaitable_result_tuple(
        self, f: Callable[[_T_co], AwaitableResultTuple[_F, _S]]
    ) -> AwaitableResultTupleWrapper[_F, _S]:
        """Apply an asynchronous function with return type
        [trcks.ResultTuple][] to the wrapped
        [collections.abc.Awaitable][] object.

        Args:
            f: The asynchronous function to be applied.

        Returns:
            A [trcks.oop.AwaitableResultTupleWrapper][] instance with
                the result of the function application.

        Example:
            >>> import asyncio
            >>> from trcks import AwaitableResultTuple
            >>> from trcks.oop import AwaitableWrapper
            >>> async def validate(
            ...     x: float,
            ... ) -> AwaitableResultTuple[str, float]:
            ...     await asyncio.sleep(0.001)
            ...     if x < 0:
            ...         return "failure", "negative value"
            ...     return "success", (x, x * 2)
            ...
            >>> wrapper = (
            ...     AwaitableWrapper
            ...     .construct(5.0)
            ...     .map_to_awaitable_result_tuple(validate)
            ... )
            >>> wrapper
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper.core_as_coroutine)
            ('success', (5.0, 10.0))
        """
        return AwaitableResultTupleWrapper.construct_successes_from_awaitable(
            self.core
        ).map_successes_to_awaitable_result_tuple(f)

    def map_to_awaitable_tuple(
        self, f: Callable[[_T_co], AwaitableTuple[_T]]
    ) -> AwaitableTupleWrapper[_T]:
        """Apply an asynchronous function returning a homogeneous [tuple][]
        to the wrapped [collections.abc.Awaitable][] object.

        Args:
            f: The asynchronous function to be applied, returning an awaitable
                homogeneous [tuple][].

        Returns:
            A new [trcks.oop.AwaitableTupleWrapper][] instance with
                the result of the function application.

        Example:
            >>> import asyncio
            >>> from trcks.oop import AwaitableWrapper
            >>> async def slowly_duplicate(n: int) -> tuple[int, ...]:
            ...     await asyncio.sleep(0.001)
            ...     return (n, n)
            ...
            >>> awaitable_tuple_wrapper = (
            ...     AwaitableWrapper
            ...     .construct(21)
            ...     .map_to_awaitable_tuple(slowly_duplicate)
            ... )
            >>> awaitable_tuple_wrapper
            AwaitableTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_tuple_wrapper.core_as_coroutine)
            (21, 21)
        """
        return AwaitableTupleWrapper(a.map_to_awaitable(f)(self.core))

    def map_to_result(
        self, f: Callable[[_T_co], Result[_F, _S]]
    ) -> AwaitableResultWrapper[_F, _S]:
        """Apply a synchronous function with return type [trcks.Result][]
        to the wrapped [collections.abc.Awaitable][] object.

        Args:
            f: The synchronous function to be applied.

        Returns:
            A [trcks.oop.AwaitableResultWrapper][] instance with
                the result of the function application.

        Example:
            >>> import asyncio
            >>> from trcks.oop import AwaitableWrapper
            >>> awaitable_result_wrapper = (
            ...     AwaitableWrapper
            ...     .construct(-1)
            ...     .map_to_result(
            ...         lambda n: (
            ...             ("success", n) if n >= 0 else ("failure", "negative value")
            ...         )
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

    def map_to_result_tuple(
        self, f: Callable[[_T_co], ResultTuple[_F, _S]]
    ) -> AwaitableResultTupleWrapper[_F, _S]:
        """Apply a synchronous function with return type [trcks.ResultTuple][]
        to the wrapped [collections.abc.Awaitable][] object.

        Args:
            f: The synchronous function to be applied.

        Returns:
            A [trcks.oop.AwaitableResultTupleWrapper][] instance with
                the result of the function application.

        Example:
            >>> import asyncio
            >>> from trcks import ResultTuple
            >>> from trcks.oop import AwaitableWrapper
            >>> def validate(x: float) -> ResultTuple[str, float]:
            ...     if x < 0:
            ...         return "failure", "negative value"
            ...     return "success", (x, x * 2)
            ...
            >>> wrapper = AwaitableWrapper.construct(5.0).map_to_result_tuple(
            ...     validate
            ... )
            >>> wrapper
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper.core_as_coroutine)
            ('success', (5.0, 10.0))
        """
        return AwaitableResultTupleWrapper.construct_successes_from_awaitable(
            self.core
        ).map_successes_to_result_tuple(f)

    def map_to_tuple(
        self, f: Callable[[_T_co], tuple[_T, ...]]
    ) -> AwaitableTupleWrapper[_T]:
        """Apply a synchronous function returning a homogeneous [tuple][]
        to the wrapped [collections.abc.Awaitable][] object.

        Args:
            f: The synchronous function to be applied.

        Returns:
            A new [trcks.oop.AwaitableTupleWrapper][] instance with
                the result of the function application.

        Example:
            >>> import asyncio
            >>> from trcks.oop import AwaitableWrapper
            >>> awaitable_tuple_wrapper = (
            ...     AwaitableWrapper
            ...     .construct(3)
            ...     .map_to_tuple(lambda n: (n, -n))
            ... )
            >>> awaitable_tuple_wrapper
            AwaitableTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_tuple_wrapper.core_as_coroutine)
            (3, -3)
        """
        return AwaitableTupleWrapper(a.map_(f)(self.core))

    def tap(self, f: Callable[[_T_co], object]) -> AwaitableWrapper[_T_co]:
        """Apply a synchronous side effect
        to the wrapped [collections.abc.Awaitable][] object.

        Args:
            f: The synchronous side effect to be applied.

        Returns:
            A new [trcks.oop.AwaitableWrapper][] instance with
                the original [collections.abc.Awaitable][] object.

        Example:
            >>> import asyncio
            >>> from trcks.oop import AwaitableWrapper
            >>> awaitable_wrapper = AwaitableWrapper.construct("Hello, world!").tap(
            ...     lambda s: print(f"String: {s}")
            ... )
            >>> value = asyncio.run(awaitable_wrapper.core_as_coroutine)
            String: Hello, world!
            >>> value
            'Hello, world!'
        """
        return AwaitableWrapper(a.tap(f)(self.core))

    def tap_to_awaitable(
        self, f: Callable[[_T_co], Awaitable[object]]
    ) -> AwaitableWrapper[_T_co]:
        """Apply an asynchronous side effect
        to the wrapped [collections.abc.Awaitable][] object.

        Args:
            f: The asynchronous side effect to be applied.

        Returns:
            A [trcks.oop.AwaitableWrapper][] instance with the original wrapped object.

        Example:
            >>> import asyncio
            >>> from trcks.oop import AwaitableWrapper
            >>> async def write_to_disk(output: str) -> None:
            ...     await asyncio.sleep(0.001)
            ...     print(f"Wrote '{output}' to disk.")
            ...
            >>> awaitable_wrapper = AwaitableWrapper.construct(
            ...     "Hello, world!"
            ... ).tap_to_awaitable(write_to_disk)
            >>> value = asyncio.run(awaitable_wrapper.core_as_coroutine)
            Wrote 'Hello, world!' to disk.
            >>> value
            'Hello, world!'
        """
        return AwaitableWrapper(a.tap_to_awaitable(f)(self.core))

    def tap_to_awaitable_result(
        self, f: Callable[[_T_co], AwaitableResult[_F, object]]
    ) -> AwaitableResultWrapper[_F, _T_co]:
        """Apply an asynchronous side effect with return type [trcks.Result][]
        to the wrapped object.

        Args:
            f: The asynchronous side effect to be applied.

        Returns:
            A [trcks.oop.AwaitableResultWrapper][] instance with

                - *the returned* [trcks.Failure][]
                    if the given side effect returns a [trcks.Failure][] or
                - a [trcks.Success][] instance containing *the original* wrapped object
                    if the given side effect returns a [trcks.Success][].

        Example:
            >>> import asyncio
            >>> from typing import Literal
            >>> from trcks import Result
            >>> from trcks.oop import AwaitableWrapper
            >>> WriteErrorLiteral = Literal["write error"]
            >>> async def write_to_disk(s: str, path: str) -> Result[
            ...     WriteErrorLiteral, None
            ... ]:
            ...     if path != "output.txt":
            ...         return "failure", "write error"
            ...     await asyncio.sleep(0.001)
            ...     print(f"Wrote '{s}' to file {path}.")
            ...     return "success", None
            ...
            >>> awaitable_wrapper_1 = AwaitableWrapper.construct(
            ...     "Hello, world!"
            ... ).tap_to_awaitable_result(lambda s: write_to_disk(s, "destination.txt"))
            >>> result_1 = asyncio.run(awaitable_wrapper_1.core_as_coroutine)
            >>> result_1
            ('failure', 'write error')
            >>> awaitable_wrapper_2 = AwaitableWrapper.construct(
            ...     "Hello, world!"
            ... ).tap_to_awaitable_result(lambda s: write_to_disk(s, "output.txt"))
            >>> result_2 = asyncio.run(awaitable_wrapper_2.core_as_coroutine)
            Wrote 'Hello, world!' to file output.txt.
            >>> result_2
            ('success', 'Hello, world!')
        """
        return AwaitableResultWrapper.construct_success_from_awaitable(
            self.core
        ).tap_success_to_awaitable_result(f)

    def tap_to_awaitable_result_tuple(
        self, f: Callable[[_T_co], AwaitableResultTuple[_F, object]]
    ) -> AwaitableResultTupleWrapper[_F, _T_co]:
        """Apply an asynchronous side effect with return type
        [trcks.ResultTuple][] to the wrapped
        [collections.abc.Awaitable][] object.

        Args:
            f: The asynchronous side effect to be applied.

        Returns:
            A [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - *the returned* [trcks.Failure][]
                    if the given side effect returns a [trcks.Failure][] or
                - *the original* wrapped object repeated once per element
                    in the side effect output if the given side effect
                    returns [trcks.SuccessTuple][].

        Example:
            >>> import asyncio
            >>> from trcks import AwaitableResultTuple
            >>> from trcks.oop import AwaitableWrapper
            >>> async def write_twice(
            ...     s: str,
            ... ) -> AwaitableResultTuple[str, None]:
            ...     await asyncio.sleep(0.001)
            ...     print(f"Wrote '{s}' twice.")
            ...     return "success", (None, None)
            ...
            >>> wrapper = AwaitableWrapper.construct(
            ...     "Hello, world!"
            ... ).tap_to_awaitable_result_tuple(write_twice)
            >>> wrapper
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> result = asyncio.run(wrapper.core_as_coroutine)
            Wrote 'Hello, world!' twice.
            >>> result
            ('success', ('Hello, world!', 'Hello, world!'))
        """
        return AwaitableResultTupleWrapper.construct_successes_from_awaitable(
            self.core
        ).tap_successes_to_awaitable_result_tuple(f)

    def tap_to_awaitable_tuple(
        self, f: Callable[[_T_co], AwaitableTuple[object]]
    ) -> AwaitableTupleWrapper[_T_co]:
        """Apply an asynchronous side effect returning a [tuple][]
        to the wrapped [collections.abc.Awaitable][] object.

        Args:
            f: The asynchronous side effect to be applied,
                returning an awaitable homogeneous [tuple][].

        Returns:
            A new [trcks.oop.AwaitableTupleWrapper][] instance with
                the original awaitable wrapped object repeated
                according to the number of items returned by the side effect.

        Example:
            >>> import asyncio
            >>> from trcks.oop import AwaitableTupleWrapper, AwaitableWrapper
            >>> async def slowly_duplicate_with_log(n: int) -> tuple[int, ...]:
            ...     await asyncio.sleep(0.001)
            ...     print(f"Processing: {n}")
            ...     return (n, n)
            ...
            >>> awaitable_tuple_wrapper: AwaitableTupleWrapper[int] = (
            ...     AwaitableWrapper
            ...     .construct(21)
            ...     .tap_to_awaitable_tuple(slowly_duplicate_with_log)
            ... )
            >>> awaitable_tuple_wrapper
            AwaitableTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_tuple_wrapper.core_as_coroutine)
            Processing: 21
            (21, 21)
        """
        return AwaitableTupleWrapper.construct_from_awaitable(
            self.core
        ).tap_to_awaitable_tuple(f)

    def tap_to_result(
        self, f: Callable[[_T_co], Result[_F, object]]
    ) -> AwaitableResultWrapper[_F, _T_co]:
        """Apply a synchronous side effect with return type [trcks.Result][]
        to the wrapped object.

        Args:
            f: The synchronous side effect to be applied.

        Returns:
            A [trcks.oop.AwaitableResultWrapper][] instance with

                - *the returned* [trcks.Failure][]
                    if the given side effect returns a [trcks.Failure][] or
                - a [trcks.Success][] instance containing *the original* wrapped object
                    if the given side effect returns a [trcks.Success][].

        Example:
            >>> import asyncio
            >>> from trcks import Result
            >>> from trcks.oop import AwaitableWrapper
            >>> def print_positive_float(x: float) -> Result[str, None]:
            ...     if x <= 0:
            ...         return "failure", "not positive"
            ...     return "success", print(f"Positive float: {x}")
            ...
            >>>
            >>> awaitable_result_wrapper_1 = AwaitableWrapper.construct(
            ...     -2.3
            ... ).tap_to_result(print_positive_float)
            >>> result_1 = asyncio.run(awaitable_result_wrapper_1.core_as_coroutine)
            >>> result_1
            ('failure', 'not positive')
            >>> awaitable_result_wrapper_2 = AwaitableWrapper.construct(
            ...     3.5
            ... ).tap_to_result(print_positive_float)
            >>> result_2 = asyncio.run(awaitable_result_wrapper_2.core_as_coroutine)
            Positive float: 3.5
            >>> result_2
            ('success', 3.5)
        """
        return AwaitableResultWrapper.construct_success_from_awaitable(
            self.core
        ).tap_success_to_result(f)

    def tap_to_result_tuple(
        self, f: Callable[[_T_co], ResultTuple[_F, object]]
    ) -> AwaitableResultTupleWrapper[_F, _T_co]:
        """Apply a synchronous side effect with return type [trcks.ResultTuple][]
        to the wrapped [collections.abc.Awaitable][] object.

        Args:
            f: The synchronous side effect to be applied.

        Returns:
            A [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - *the returned* [trcks.Failure][]
                    if the given side effect returns a [trcks.Failure][] or
                - *the original* wrapped object repeated once per element
                    in the side effect output if the given side effect
                    returns [trcks.SuccessTuple][].

        Example:
            >>> import asyncio
            >>> from trcks import ResultTuple
            >>> from trcks.oop import AwaitableWrapper
            >>> def write_twice(s: str) -> ResultTuple[str, None]:
            ...     print(f"Wrote '{s}' twice.")
            ...     return "success", (None, None)
            ...
            >>> wrapper = AwaitableWrapper.construct(
            ...     "Hello, world!"
            ... ).tap_to_result_tuple(write_twice)
            >>> wrapper
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> result = asyncio.run(wrapper.core_as_coroutine)
            Wrote 'Hello, world!' twice.
            >>> result
            ('success', ('Hello, world!', 'Hello, world!'))
        """
        return AwaitableResultTupleWrapper.construct_successes_from_awaitable(
            self.core
        ).tap_successes_to_result_tuple(f)

    def tap_to_tuple(
        self, f: Callable[[_T_co], tuple[object, ...]]
    ) -> AwaitableTupleWrapper[_T_co]:
        """Apply a synchronous side effect returning a [tuple][]
        to the wrapped [collections.abc.Awaitable][] object.

        Args:
            f: The synchronous side effect to be applied,
                returning a homogeneous [tuple][].

        Returns:
            A new [trcks.oop.AwaitableTupleWrapper][] instance with
                the original awaitable wrapped object repeated
                according to the number of items returned by the side effect.

        Example:
            >>> import asyncio
            >>> from trcks.oop import AwaitableTupleWrapper, AwaitableWrapper
            >>> def duplicate_with_log(n: int) -> tuple[object, ...]:
            ...     print(f"Processing: {n}")
            ...     return (n, n)
            ...
            >>> awaitable_tuple_wrapper: AwaitableTupleWrapper[int] = (
            ...     AwaitableWrapper
            ...     .construct(42)
            ...     .tap_to_tuple(duplicate_with_log)
            ... )
            >>> awaitable_tuple_wrapper
            AwaitableTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_tuple_wrapper.core_as_coroutine)
            Processing: 42
            (42, 42)
        """
        return AwaitableTupleWrapper.construct_from_awaitable(self.core).tap_to_tuple(f)


class ResultWrapper(_ResultWrapper[_F_default_co, _S_default_co]):
    """Type-safe and immutable wrapper for [trcks.Result][] objects.

    The wrapped object can be accessed via the attribute `trcks.oop.ResultWrapper.core`.
    The `trcks.oop.ResultWrapper.map*` methods allow method chaining.
    The `trcks.oop.ResultWrapper.tap*` methods allow for side effects.

    Example:
        >>> import math
        >>> from trcks.oop import ResultWrapper
        >>> result_wrapper = (
        ...     ResultWrapper
        ...     .construct_success(-5.0)
        ...     .map_success_to_result(
        ...         lambda x: (
        ...             ("success", x) if x >= 0 else ("failure", "negative value")
        ...         )
        ...     )
        ...     .tap_failure(lambda flr: print(f"Failure '{flr}' occurred."))
        ...     .map_success(math.sqrt)
        ... )
        Failure 'negative value' occurred.
        >>> result_wrapper
        ResultWrapper(core=('failure', 'negative value'))
        >>> result_wrapper.core
        ('failure', 'negative value')
    """

    @staticmethod
    def construct_failure(value: _F) -> ResultWrapper[_F, Never]:
        """Construct and wrap a [trcks.Failure][] object from a value.

        Args:
            value: The value to be wrapped.

        Returns:
            A new [trcks.oop.ResultWrapper][] instance
                with the wrapped [trcks.Failure][] object.

        Example:
            >>> ResultWrapper.construct_failure(42)
            ResultWrapper(core=('failure', 42))
        """
        return ResultWrapper(r.construct_failure(value))

    @staticmethod
    def construct_from_result(
        rslt: Result[_F_default, _S_default],
    ) -> ResultWrapper[_F_default, _S_default]:
        """Wrap a [trcks.Result][] object.

        Args:
            rslt: The [trcks.Result][] object to be wrapped.

        Returns:
            A new [trcks.oop.ResultWrapper][] instance
                with the wrapped [trcks.Result][] object.

        Example:
            >>> ResultWrapper.construct_from_result(("success", 0.0))
            ResultWrapper(core=('success', 0.0))
        """
        return ResultWrapper(rslt)

    @staticmethod
    def construct_success(value: _S) -> ResultWrapper[Never, _S]:
        """Construct and wrap a [trcks.Success][] object from a value.

        Args:
            value: The value to be wrapped.

        Returns:
            A new [trcks.oop.ResultWrapper][] instance with
                the wrapped [trcks.Success][] object.

        Example:
            >>> ResultWrapper.construct_success(42)
            ResultWrapper(core=('success', 42))
        """
        return ResultWrapper(r.construct_success(value))

    def map_failure(
        self, f: Callable[[_F_default_co], _F]
    ) -> ResultWrapper[_F, _S_default_co]:
        """Apply a synchronous function to the wrapped [trcks.Failure][] object.

        Wrapped [trcks.Success][] objects are passed on unchanged.

        Args:
            f: The synchronous function to be applied.

        Returns:
            A new [trcks.oop.ResultWrapper][] instance with

                - the result of the function application if
                    the original [trcks.Result][] is a failure, or
                - the original [trcks.Result][] object if it is a success.

        Example:
            >>> ResultWrapper.construct_failure("negative value").map_failure(
            ...     lambda s: f"Prefix: {s}"
            ... )
            ResultWrapper(core=('failure', 'Prefix: negative value'))
            >>>
            >>> ResultWrapper.construct_success(25.0).map_failure(
            ...     lambda s: f"Prefix: {s}"
            ... )
            ResultWrapper(core=('success', 25.0))
        """
        return ResultWrapper(r.map_failure(f)(self.core))

    def map_failure_to_awaitable(
        self, f: Callable[[_F_default_co], Awaitable[_F]]
    ) -> AwaitableResultWrapper[_F, _S_default_co]:
        """Apply an asynchronous function to the wrapped [trcks.Failure][] object.

        Wrapped [trcks.Success][] objects are passed on unchanged.

        Args:
            f: The asynchronous function to be applied.

        Returns:
            A [trcks.oop.AwaitableResultWrapper][] instance with

                - the result of the function application if
                    the original [trcks.Result][] is a failure, or
                - the original [trcks.Result][] object if it is a success.

        Example:
            >>> import asyncio
            >>> from trcks.oop import ResultWrapper
            >>> async def add_prefix_slowly(s: str) -> str:
            ...     await asyncio.sleep(0.001)
            ...     return f"Prefix: {s}"
            ...
            >>> awaitable_result_wrapper_1 = (
            ...     ResultWrapper
            ...     .construct_failure("not found")
            ...     .map_failure_to_awaitable(add_prefix_slowly)
            ... )
            >>> awaitable_result_wrapper_1
            AwaitableResultWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_result_wrapper_1.core_as_coroutine)
            ('failure', 'Prefix: not found')
            >>>
            >>> awaitable_result_wrapper_2 = (
            ...     ResultWrapper
            ...     .construct_success(42)
            ...     .map_failure_to_awaitable(add_prefix_slowly)
            ... )
            >>> awaitable_result_wrapper_2
            AwaitableResultWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_result_wrapper_2.core_as_coroutine)
            ('success', 42)
        """
        return AwaitableResultWrapper.construct_from_result(
            self.core
        ).map_failure_to_awaitable(f)

    def map_failure_to_awaitable_result(
        self, f: Callable[[_F_default_co], AwaitableResult[_F, _S]]
    ) -> AwaitableResultWrapper[_F, _S_default_co | _S]:
        """Apply an asynchronous function with return type [trcks.Result][]
        to the wrapped [trcks.Failure][] object.

        Wrapped [trcks.Success][] objects are passed on unchanged.

        Args:
            f: The asynchronous function to be applied.

        Returns:
            A [trcks.oop.AwaitableResultWrapper][] instance with

                - the result of the function application if
                    the original [trcks.Result][] is a failure, or
                - the original [trcks.Result][] object if it is a success.

        Example:
            >>> import asyncio
            >>> from trcks import Result
            >>> from trcks.oop import ResultWrapper
            >>> async def slowly_replace_not_found(s: str) -> Result[str, float]:
            ...     await asyncio.sleep(0.001)
            ...     if s == "not found":
            ...         return "success", 0.0
            ...     return "failure", s
            ...
            >>> awaitable_result_wrapper_1 = (
            ...     ResultWrapper
            ...     .construct_failure("not found")
            ...     .map_failure_to_awaitable_result(slowly_replace_not_found)
            ... )
            >>> awaitable_result_wrapper_1
            AwaitableResultWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_result_wrapper_1.core_as_coroutine)
            ('success', 0.0)
            >>>
            >>> awaitable_result_wrapper_2 = (
            ...     ResultWrapper
            ...     .construct_failure("other failure")
            ...     .map_failure_to_awaitable_result(slowly_replace_not_found)
            ... )
            >>> awaitable_result_wrapper_2
            AwaitableResultWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_result_wrapper_2.core_as_coroutine)
            ('failure', 'other failure')
            >>>
            >>> awaitable_result_wrapper_3 = (
            ...     ResultWrapper
            ...     .construct_success(25.0)
            ...     .map_failure_to_awaitable_result(slowly_replace_not_found)
            ... )
            >>> awaitable_result_wrapper_3
            AwaitableResultWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_result_wrapper_3.core_as_coroutine)
            ('success', 25.0)
        """
        return AwaitableResultWrapper.construct_from_result(
            self.core
        ).map_failure_to_awaitable_result(f)

    def map_failure_to_awaitable_result_tuple(
        self, f: Callable[[_F_default_co], AwaitableResultTuple[_F, _S]]
    ) -> AwaitableResultTupleWrapper[_F, _S_default_co | _S]:
        """Apply an asynchronous function with return type
        [trcks.ResultTuple][] to the wrapped [trcks.Failure][] object.

        Wrapped [trcks.Success][] objects are passed on unchanged.

        Args:
            f: The asynchronous function to be applied.

        Returns:
            A [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - the result of the function application if
                    the original [trcks.Result][] is a failure, or
                - the original [trcks.Result][] object if it is a success.

        Example:
            >>> import asyncio
            >>> from trcks import AwaitableResultTuple
            >>> from trcks.oop import ResultWrapper
            >>> async def recover(
            ...     e: str,
            ... ) -> AwaitableResultTuple[str, float]:
            ...     await asyncio.sleep(0.001)
            ...     if e == "not found":
            ...         return "success", (0.0, 1.0)
            ...     return "failure", e
            ...
            >>> wrapper_1 = (
            ...     ResultWrapper
            ...     .construct_failure("not found")
            ...     .map_failure_to_awaitable_result_tuple(recover)
            ... )
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('success', (0.0, 1.0))
            >>>
            >>> wrapper_2 = (
            ...     ResultWrapper
            ...     .construct_success(25.0)
            ...     .map_failure_to_awaitable_result_tuple(recover)
            ... )
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('success', (25.0,))
        """
        return AwaitableResultTupleWrapper.construct_from_result(
            self.core
        ).map_failure_to_awaitable_result_tuple(f)

    def map_failure_to_result(
        self, f: Callable[[_F_default_co], Result[_F, _S]]
    ) -> ResultWrapper[_F, _S_default_co | _S]:
        """Apply a synchronous function with return type [trcks.Result][]
        to the wrapped [trcks.Failure][] object.

        Wrapped [trcks.Success][] objects are passed on unchanged.

        Args:
            f: The synchronous function to be applied.

        Returns:
            A new [trcks.oop.ResultWrapper][] instance with

                - the result of the function application if
                    the original [trcks.Result][] is a failure, or
                - the original [trcks.Result][] object if it is a success.

        Example:
            >>> from trcks import Result
            >>> from trcks.oop import ResultWrapper
            >>> def replace_not_found_by_default_value(s: str) -> Result[str, float]:
            ...     if s == "not found":
            ...         return "success", 0.0
            ...     return "failure", s
            ...
            >>> ResultWrapper.construct_failure(
            ...     "not found"
            ... ).map_failure_to_result(
            ...     replace_not_found_by_default_value
            ... )
            ResultWrapper(core=('success', 0.0))
            >>>
            >>> ResultWrapper.construct_failure(
            ...     "other failure"
            ... ).map_failure_to_result(
            ...     replace_not_found_by_default_value
            ... )
            ResultWrapper(core=('failure', 'other failure'))
            >>>
            >>> ResultWrapper.construct_success(
            ...     25.0
            ... ).map_failure_to_result(
            ...     replace_not_found_by_default_value
            ... )
            ResultWrapper(core=('success', 25.0))
        """
        return ResultWrapper(r.map_failure_to_result(f)(self.core))

    def map_failure_to_result_tuple(
        self, f: Callable[[_F_default_co], ResultTuple[_F, _S]]
    ) -> ResultTupleWrapper[_F, _S_default_co | _S]:
        """Apply a synchronous function with return type [trcks.ResultTuple][]
        to the wrapped [trcks.Failure][] object.

        Wrapped [trcks.Success][] objects are passed on unchanged.

        Args:
            f: The synchronous function to be applied.

        Returns:
            A [trcks.oop.ResultTupleWrapper][] instance with

                - the result of the function application if
                    the original [trcks.Result][] is a failure, or
                - the original [trcks.Result][] object (wrapped as a tuple)
                    if it is a success.

        Example:
            >>> from trcks import ResultTuple
            >>> from trcks.oop import ResultWrapper
            >>> def expand_error(s: str) -> ResultTuple[str, float]:
            ...     if s == "not found":
            ...         return "success", (0.0, 1.0)
            ...     return "failure", s
            ...
            >>> ResultWrapper.construct_failure(
            ...     "not found"
            ... ).map_failure_to_result_tuple(expand_error)
            ResultTupleWrapper(core=('success', (0.0, 1.0)))
            >>>
            >>> ResultWrapper.construct_failure(
            ...     "other error"
            ... ).map_failure_to_result_tuple(expand_error)
            ResultTupleWrapper(core=('failure', 'other error'))
            >>>
            >>> ResultWrapper.construct_success(
            ...     42
            ... ).map_failure_to_result_tuple(expand_error)
            ResultTupleWrapper(core=('success', (42,)))
        """
        return ResultTupleWrapper.construct_from_result(
            self.core
        ).map_failure_to_result_tuple(f)

    def map_failure_to_tuple(
        self, f: Callable[[_F_default_co], tuple[_S, ...]]
    ) -> ResultTupleWrapper[Never, _S_default_co | _S]:
        """Apply a synchronous function returning a homogeneous [tuple][]
        to the wrapped [trcks.Failure][] object.

        The failure is converted to a [trcks.SuccessTuple][].
        Wrapped [trcks.Success][] objects are passed on unchanged.

        Args:
            f: The synchronous function to be applied,
                returning a homogeneous [tuple][].

        Returns:
            A [trcks.oop.ResultTupleWrapper][] instance with

                - a [trcks.SuccessTuple][] containing the result
                    of the function application if
                    the original [trcks.Result][] is a failure, or
                - the original [trcks.Result][] object (wrapped as a tuple)
                    if it is a success.

        Example:
            >>> from trcks.oop import ResultWrapper
            >>> def recover(s: str) -> tuple[float, ...]:
            ...     if s == "not found":
            ...         return (0.0, 1.0)
            ...     return ()
            ...
            >>> ResultWrapper.construct_failure(
            ...     "not found"
            ... ).map_failure_to_tuple(recover)
            ResultTupleWrapper(core=('success', (0.0, 1.0)))
            >>>
            >>> ResultWrapper.construct_failure(
            ...     "other error"
            ... ).map_failure_to_tuple(recover)
            ResultTupleWrapper(core=('success', ()))
            >>>
            >>> ResultWrapper.construct_success(
            ...     42
            ... ).map_failure_to_tuple(recover)
            ResultTupleWrapper(core=('success', (42,)))
        """
        return ResultTupleWrapper.construct_from_result(self.core).map_failure_to_tuple(
            f
        )

    def map_success(
        self, f: Callable[[_S_default_co], _S]
    ) -> ResultWrapper[_F_default_co, _S]:
        """Apply a synchronous function to the wrapped [trcks.Success][] object.

        Wrapped [trcks.Failure][] objects are passed on unchanged.

        Args:
            f: The synchronous function to be applied.

        Returns:
            A new [trcks.oop.ResultWrapper][] instance with

                - the original [trcks.Result][] object if it is a failure, or
                - the result of the function application if
                    the original [trcks.Result][] is a success.

        Example:
            >>> ResultWrapper.construct_failure("not found").map_success(lambda n: n+1)
            ResultWrapper(core=('failure', 'not found'))
            >>>
            >>> ResultWrapper.construct_success(42).map_success(lambda n: n+1)
            ResultWrapper(core=('success', 43))
        """
        return ResultWrapper(r.map_success(f)(self.core))

    def map_success_to_awaitable(
        self, f: Callable[[_S_default_co], Awaitable[_S]]
    ) -> AwaitableResultWrapper[_F_default_co, _S]:
        """Apply an asynchronous function to the wrapped [trcks.Success][] object.

        Wrapped [trcks.Failure][] objects are passed on unchanged.

        Args:
            f: The asynchronous function to be applied.

        Returns:
            A [trcks.oop.AwaitableResultWrapper][] instance with

                - the original [trcks.Result][] object if it is a failure, or
                - the result of the function application if
                    the original [trcks.Result][] is a success.

        Example:
            >>> import asyncio
            >>> from trcks.oop import ResultWrapper
            >>> async def increment_slowly(n: int) -> int:
            ...     await asyncio.sleep(0.001)
            ...     return n + 1
            ...
            >>> awaitable_result_wrapper_1 = (
            ...     ResultWrapper
            ...     .construct_failure("not found")
            ...     .map_success_to_awaitable(increment_slowly)
            ... )
            >>> awaitable_result_wrapper_1
            AwaitableResultWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_result_wrapper_1.core_as_coroutine)
            ('failure', 'not found')
            >>>
            >>> awaitable_result_wrapper_2 = (
            ...     ResultWrapper
            ...     .construct_success(42)
            ...     .map_success_to_awaitable(increment_slowly)
            ... )
            >>> awaitable_result_wrapper_2
            AwaitableResultWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_result_wrapper_2.core_as_coroutine)
            ('success', 43)
        """
        return AwaitableResultWrapper.construct_from_result(
            self.core
        ).map_success_to_awaitable(f)

    def map_success_to_awaitable_result(
        self, f: Callable[[_S_default_co], AwaitableResult[_F, _S]]
    ) -> AwaitableResultWrapper[_F_default_co | _F, _S]:
        """Apply an asynchronous function with return type [trcks.Result][]
        to the wrapped [trcks.Success][] object.

        Wrapped [trcks.Failure][] objects are passed on unchanged.

        Args:
            f: The asynchronous function to be applied.

        Returns:
            A [trcks.oop.AwaitableResultWrapper][] instance with

                - the original [trcks.Result][] object if it is a failure, or
                - the result of the function application if
                    the original [trcks.Result][] is a success.

        Example:
            >>> import asyncio
            >>> import math
            >>> from trcks import Result
            >>> from trcks.oop import ResultWrapper
            >>> async def get_square_root_slowly(x: float) -> Result[str, float]:
            ...     await asyncio.sleep(0.001)
            ...     if x < 0:
            ...         return "failure", "negative value"
            ...     return "success", math.sqrt(x)
            ...
            >>> awaitable_result_wrapper_1 = (
            ...     ResultWrapper
            ...     .construct_failure("not found")
            ...     .map_success_to_awaitable_result(get_square_root_slowly)
            ... )
            >>> awaitable_result_wrapper_1
            AwaitableResultWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_result_wrapper_1.core_as_coroutine)
            ('failure', 'not found')
            >>>
            >>> awaitable_result_wrapper_2 = (
            ...     ResultWrapper
            ...     .construct_success(-25.0)
            ...     .map_success_to_awaitable_result(get_square_root_slowly)
            ... )
            >>> awaitable_result_wrapper_2
            AwaitableResultWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_result_wrapper_2.core_as_coroutine)
            ('failure', 'negative value')
            >>>
            >>> awaitable_result_wrapper_3 = (
            ...     ResultWrapper
            ...     .construct_success(25.0)
            ...     .map_success_to_awaitable_result(get_square_root_slowly)
            ... )
            >>> awaitable_result_wrapper_3
            AwaitableResultWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_result_wrapper_3.core_as_coroutine)
            ('success', 5.0)
        """
        return AwaitableResultWrapper.construct_from_result(
            self.core
        ).map_success_to_awaitable_result(f)

    def map_success_to_awaitable_result_tuple(
        self, f: Callable[[_S_default_co], AwaitableResultTuple[_F, _S]]
    ) -> AwaitableResultTupleWrapper[_F_default_co | _F, _S]:
        """Apply an asynchronous function with return type
        [trcks.ResultTuple][] to the wrapped [trcks.Success][] object.

        Wrapped [trcks.Failure][] objects are passed on unchanged.

        Args:
            f: The asynchronous function to be applied.

        Returns:
            A [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - the original [trcks.Result][] object if it is a failure, or
                - the result of the function application if
                    the original [trcks.Result][] is a success.

        Example:
            >>> import asyncio
            >>> from trcks import AwaitableResultTuple
            >>> from trcks.oop import ResultWrapper
            >>> async def slowly_expand(
            ...     x: float,
            ... ) -> AwaitableResultTuple[str, float]:
            ...     await asyncio.sleep(0.001)
            ...     if x < 0:
            ...         return "failure", "negative"
            ...     return "success", (x, x * 2)
            ...
            >>> wrapper_1 = (
            ...     ResultWrapper
            ...     .construct_failure("not found")
            ...     .map_success_to_awaitable_result_tuple(slowly_expand)
            ... )
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('failure', 'not found')
            >>>
            >>> wrapper_2 = (
            ...     ResultWrapper
            ...     .construct_success(5.0)
            ...     .map_success_to_awaitable_result_tuple(slowly_expand)
            ... )
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('success', (5.0, 10.0))
        """
        return AwaitableResultTupleWrapper.construct_from_result(
            self.core
        ).map_successes_to_awaitable_result_tuple(f)

    def map_success_to_result(
        self, f: Callable[[_S_default_co], Result[_F, _S]]
    ) -> ResultWrapper[_F_default_co | _F, _S]:
        """Apply a synchronous function with return type [trcks.Result][]
        to the wrapped [trcks.Success][] object.

        Wrapped [trcks.Failure][] objects are passed on unchanged.

        Args:
            f: The synchronous function to be applied.

        Returns:
            A new [trcks.oop.ResultWrapper][] instance with

                - the original [trcks.Result][] object if it is a failure, or
                - the result of the function application if
                    the original [trcks.Result][] is a success.

        Example:
            >>> import math
            >>> from trcks import Result
            >>> from trcks.oop import ResultWrapper
            >>> def get_square_root(x: float) -> Result[str, float]:
            ...     if x < 0:
            ...         return "failure", "negative value"
            ...     return "success", math.sqrt(x)
            ...
            >>> ResultWrapper.construct_failure("not found").map_success_to_result(
            ...     get_square_root
            ... )
            ResultWrapper(core=('failure', 'not found'))
            >>>
            >>> ResultWrapper.construct_success(-25.0).map_success_to_result(
            ...     get_square_root
            ... )
            ResultWrapper(core=('failure', 'negative value'))
            >>>
            >>> ResultWrapper.construct_success(25.0).map_success_to_result(
            ...     get_square_root
            ... )
            ResultWrapper(core=('success', 5.0))
        """
        return ResultWrapper(r.map_success_to_result(f)(self.core))

    def map_success_to_result_tuple(
        self, f: Callable[[_S_default_co], ResultTuple[_F, _S]]
    ) -> ResultTupleWrapper[_F_default_co | _F, _S]:
        """Apply a synchronous function with return type [trcks.ResultTuple][]
        to the wrapped [trcks.Success][] object.

        Wrapped [trcks.Failure][] objects are passed on unchanged.

        Args:
            f: The synchronous function to be applied.

        Returns:
            A [trcks.oop.ResultTupleWrapper][] instance with

                - the original [trcks.Result][] object if it is a failure, or
                - the result of the function application if
                    the original [trcks.Result][] is a success.

        Example:
            >>> from trcks import ResultTuple
            >>> from trcks.oop import ResultWrapper
            >>> def expand(x: float) -> ResultTuple[str, float]:
            ...     if x < 0:
            ...         return "failure", "negative"
            ...     return "success", (x, x * 2)
            ...
            >>> ResultWrapper.construct_failure(
            ...     "not found"
            ... ).map_success_to_result_tuple(expand)
            ResultTupleWrapper(core=('failure', 'not found'))
            >>>
            >>> ResultWrapper.construct_success(
            ...     5.0
            ... ).map_success_to_result_tuple(expand)
            ResultTupleWrapper(core=('success', (5.0, 10.0)))
            >>>
            >>> ResultWrapper.construct_success(
            ...     -5.0
            ... ).map_success_to_result_tuple(expand)
            ResultTupleWrapper(core=('failure', 'negative'))
        """
        return ResultTupleWrapper.construct_from_result(
            self.core
        ).map_successes_to_result_tuple(f)

    def map_success_to_tuple(
        self, f: Callable[[_S_default_co], tuple[_S, ...]]
    ) -> ResultTupleWrapper[_F_default_co, _S]:
        """Apply a synchronous function returning a homogeneous [tuple][]
        to the wrapped [trcks.Success][] object.

        Wrapped [trcks.Failure][] objects are passed on unchanged.

        Args:
            f: The synchronous function to be applied,
                returning a homogeneous [tuple][].

        Returns:
            A [trcks.oop.ResultTupleWrapper][] instance with

                - the original [trcks.Result][] object if it is a failure, or
                - a [trcks.SuccessTuple][] containing the result
                    of the function application if
                    the original [trcks.Result][] is a success.

        Example:
            >>> from trcks.oop import ResultWrapper
            >>> def duplicate(x: float) -> tuple[float, ...]:
            ...     return (x, x)
            ...
            >>> ResultWrapper.construct_failure(
            ...     "not found"
            ... ).map_success_to_tuple(duplicate)
            ResultTupleWrapper(core=('failure', 'not found'))
            >>>
            >>> ResultWrapper.construct_success(
            ...     5.0
            ... ).map_success_to_tuple(duplicate)
            ResultTupleWrapper(core=('success', (5.0, 5.0)))
        """
        return ResultTupleWrapper.construct_from_result(
            self.core
        ).map_successes_to_tuple(f)

    def tap_failure(
        self, f: Callable[[_F_default_co], object]
    ) -> ResultWrapper[_F_default_co, _S_default_co]:
        """Apply a synchronous side effect to the wrapped [trcks.Failure][] object.

        Wrapped [trcks.Success][] objects are passed on without side effects.

        Args:
            f: The synchronous side effect to be applied.

        Returns:
            A new [trcks.oop.ResultWrapper][] instance
                with the original [trcks.Result][] object,
                allowing for further method chaining.

        Example:
            >>> result_wrapper_1 = ResultWrapper.construct_failure(
            ...     "not found"
            ... ).tap_failure(lambda f: print(f"Failure: {f}"))
            Failure: not found
            >>> result_wrapper_1
            ResultWrapper(core=('failure', 'not found'))
            >>> result_wrapper_2 = ResultWrapper.construct_success(42).tap_failure(
            ...     lambda f: print(f"Failure: {f}")
            ... )
            >>> result_wrapper_2
            ResultWrapper(core=('success', 42))
        """
        return ResultWrapper(r.tap_failure(f)(self.core))

    def tap_failure_to_awaitable(
        self, f: Callable[[_F_default_co], Awaitable[object]]
    ) -> AwaitableResultWrapper[_F_default_co, _S_default_co]:
        """Apply an asynchronous side effect to the wrapped [trcks.Failure][] object.

        Wrapped [trcks.Success][] objects are passed on without side effects.

        Args:
            f: The asynchronous side effect to be applied.

        Returns:
            A [trcks.oop.AwaitableResultWrapper][] instance
                with the original [trcks.Result][] object,
                allowing for further method chaining.

        Example:
            >>> import asyncio
            >>> from trcks.oop import ResultWrapper
            >>> async def write_to_disk(output: str) -> None:
            ...     await asyncio.sleep(0.001)
            ...     print(f"Wrote '{output}' to disk.")
            ...
            >>> awaitable_result_wrapper_1 = ResultWrapper.construct_failure(
            ...     "not found"
            ... ).tap_failure_to_awaitable(write_to_disk)
            >>> awaitable_result_wrapper_1
            AwaitableResultWrapper(core=<coroutine object ...>)
            >>> result_1 = asyncio.run(awaitable_result_wrapper_1.core_as_coroutine)
            Wrote 'not found' to disk.
            >>> result_1
            ('failure', 'not found')
            >>> awaitable_result_wrapper_2 = ResultWrapper.construct_success(
            ...     42
            ... ).tap_failure_to_awaitable(write_to_disk)
            >>> awaitable_result_wrapper_2
            AwaitableResultWrapper(core=<coroutine object ...>)
            >>> result_2 = asyncio.run(awaitable_result_wrapper_2.core_as_coroutine)
            >>> result_2
            ('success', 42)
        """
        return AwaitableResultWrapper.construct_from_result(
            self.core
        ).tap_failure_to_awaitable(f)

    def tap_failure_to_awaitable_result(
        self, f: Callable[[_F_default_co], AwaitableResult[object, _S]]
    ) -> AwaitableResultWrapper[_F_default_co, _S_default_co | _S]:
        """Apply an asynchronous side effect with return type [trcks.Result][]
        to the wrapped [trcks.Failure][] object.

        Wrapped [trcks.Success][] objects are passed on without side effects.

        Args:
            f: The asynchronous side effect to be applied.

        Returns:
            A [trcks.oop.AwaitableResultWrapper][] instance with

                - *the original* [trcks.Failure][]
                    if the applied side effect returns a [trcks.Failure][],
                - *the returned* [trcks.Success][]
                    if the applied side effect returns a [trcks.Success][] and
                - *the original* [trcks.Success][] if no side effect was applied.

        Example:
            >>> import asyncio
            >>> from trcks import Result
            >>> from trcks.oop import ResultWrapper
            >>> async def replace_not_found_with_default(
            ...     s: str
            ... ) -> Result[object, float]:
            ...     await asyncio.sleep(0.001)
            ...     if s == "not found":
            ...         return "success", 0.0
            ...     return "failure", s
            ...
            >>> awaitable_result_wrapper_1 = (
            ...     ResultWrapper
            ...     .construct_failure("not found")
            ...     .tap_failure_to_awaitable_result(replace_not_found_with_default)
            ... )
            >>> result_1 = asyncio.run(awaitable_result_wrapper_1.core_as_coroutine)
            >>> result_1
            ('success', 0.0)
            >>> awaitable_result_wrapper_2 = (
            ...     ResultWrapper
            ...     .construct_failure("other error")
            ...     .tap_failure_to_awaitable_result(replace_not_found_with_default)
            ... )
            >>> result_2 = asyncio.run(awaitable_result_wrapper_2.core_as_coroutine)
            >>> result_2
            ('failure', 'other error')
            >>> awaitable_result_wrapper_3 = (
            ...     ResultWrapper
            ...     .construct_success(42)
            ...     .tap_failure_to_awaitable_result(replace_not_found_with_default)
            ... )
            >>> result_3 = asyncio.run(awaitable_result_wrapper_3.core_as_coroutine)
            >>> result_3
            ('success', 42)
        """
        return AwaitableResultWrapper.construct_from_result(
            self.core
        ).tap_failure_to_awaitable_result(f)

    def tap_failure_to_awaitable_result_tuple(
        self, f: Callable[[_F_default_co], AwaitableResultTuple[object, _S]]
    ) -> AwaitableResultTupleWrapper[_F_default_co, _S_default_co | _S]:
        """Apply an asynchronous side effect with return type
        [trcks.ResultTuple][] to the wrapped [trcks.Failure][] object.

        Wrapped [trcks.Success][] objects are passed on without side effects.

        Args:
            f: The asynchronous side effect to be applied.

        Returns:
            A [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - *the original* [trcks.Failure][]
                    if the applied side effect returns a [trcks.Failure][],
                - *the returned* [trcks.SuccessTuple][]
                    if the applied side effect returns a [trcks.SuccessTuple][]
                    and
                - *the original* [trcks.Success][] if no side effect was applied.

        Example:
            >>> import asyncio
            >>> from trcks import AwaitableResultTuple
            >>> from trcks.oop import ResultWrapper
            >>> async def recover(
            ...     e: str,
            ... ) -> AwaitableResultTuple[object, float]:
            ...     await asyncio.sleep(0.001)
            ...     if e == "not found":
            ...         return "success", (0.0, 1.0)
            ...     return "failure", e
            ...
            >>> wrapper_1 = (
            ...     ResultWrapper
            ...     .construct_failure("not found")
            ...     .tap_failure_to_awaitable_result_tuple(recover)
            ... )
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('success', (0.0, 1.0))
            >>>
            >>> wrapper_2 = (
            ...     ResultWrapper
            ...     .construct_success(42)
            ...     .tap_failure_to_awaitable_result_tuple(recover)
            ... )
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('success', (42,))
        """
        return AwaitableResultTupleWrapper.construct_from_result(
            self.core
        ).tap_failure_to_awaitable_result_tuple(f)

    def tap_failure_to_result(
        self, f: Callable[[_F_default_co], Result[object, _S]]
    ) -> ResultWrapper[_F_default_co, _S_default_co | _S]:
        """Apply a synchronous side effect with return type [trcks.Result][]
        to the wrapped [trcks.Failure][] object.

        Wrapped [trcks.Success][] objects are passed on without side effects.

        Args:
            f: The synchronous side effect to be applied.

        Returns:
            A new [trcks.oop.ResultWrapper][] instance with

                - *the original* [trcks.Failure][]
                    if the applied side effect returns a [trcks.Failure][],
                - *the returned* [trcks.Success][]
                    if the applied side effect returns a [trcks.Success][] and
                - *the original* [trcks.Success][] if no side effect was applied.

        Example:
            >>> from trcks import Result
            >>> from trcks.oop import ResultWrapper
            >>> def replace_not_found_with_default(s: str) -> Result[object, float]:
            ...     if s == "not found":
            ...         return "success", 0.0
            ...     return "failure", s
            ...
            >>> result_wrapper_1 = ResultWrapper.construct_failure(
            ...     "not found"
            ... ).tap_failure_to_result(replace_not_found_with_default)
            >>> result_wrapper_1
            ResultWrapper(core=('success', 0.0))
            >>> result_wrapper_2 = ResultWrapper.construct_failure(
            ...     "other error"
            ... ).tap_failure_to_result(replace_not_found_with_default)
            >>> result_wrapper_2
            ResultWrapper(core=('failure', 'other error'))
            >>> result_wrapper_3 = ResultWrapper.construct_success(
            ...     42
            ... ).tap_failure_to_result(replace_not_found_with_default)
            >>> result_wrapper_3
            ResultWrapper(core=('success', 42))
        """
        return ResultWrapper(r.tap_failure_to_result(f)(self.core))

    def tap_failure_to_result_tuple(
        self, f: Callable[[_F_default_co], ResultTuple[object, _S]]
    ) -> ResultTupleWrapper[_F_default_co, _S_default_co | _S]:
        """Apply a synchronous side effect with return type [trcks.ResultTuple][]
        to the wrapped [trcks.Failure][] object.

        Wrapped [trcks.Success][] objects are passed on without side effects.

        Args:
            f: The synchronous side effect to be applied.

        Returns:
            A [trcks.oop.ResultTupleWrapper][] instance with

                - *the original* [trcks.Failure][]
                    if the applied side effect returns a [trcks.Failure][],
                - *the returned* [trcks.SuccessTuple][]
                    if the applied side effect returns a [trcks.SuccessTuple][] and
                - *the original* [trcks.Success][] (wrapped as a tuple)
                    if no side effect was applied.

        Example:
            >>> from trcks import ResultTuple
            >>> from trcks.oop import ResultWrapper
            >>> def attempt_recover(s: str) -> ResultTuple[None, int]:
            ...     if s == "retry":
            ...         return "success", (99,)
            ...     return "failure", None
            ...
            >>> ResultWrapper.construct_failure(
            ...     "retry"
            ... ).tap_failure_to_result_tuple(attempt_recover)
            ResultTupleWrapper(core=('success', (99,)))
            >>>
            >>> ResultWrapper.construct_failure(
            ...     "fatal"
            ... ).tap_failure_to_result_tuple(attempt_recover)
            ResultTupleWrapper(core=('failure', 'fatal'))
            >>>
            >>> ResultWrapper.construct_success(
            ...     42
            ... ).tap_failure_to_result_tuple(attempt_recover)
            ResultTupleWrapper(core=('success', (42,)))
        """
        return ResultTupleWrapper.construct_from_result(
            self.core
        ).tap_failure_to_result_tuple(f)

    def tap_failure_to_tuple(
        self, f: Callable[[_F_default_co], tuple[object, ...]]
    ) -> ResultTupleWrapper[Never, _F_default_co | _S_default_co]:
        """Apply a synchronous side effect returning a [tuple][]
        to the wrapped [trcks.Failure][] object.

        The failure is converted to a [trcks.SuccessTuple][] where
        the original failure value is repeated once per element in
        the tuple returned by the side effect.

        Wrapped [trcks.Success][] objects are passed on without side effects.

        Args:
            f: The synchronous side effect to be applied,
                returning a homogeneous [tuple][].

        Returns:
            A [trcks.oop.ResultTupleWrapper][] instance with

                - a [trcks.SuccessTuple][] containing the original failure
                    repeated once per element
                    in the tuple returned by the side effect
                    if the original [trcks.Result][] is a failure, or
                - *the original* [trcks.Success][] (wrapped as a tuple)
                    if no side effect was applied.

        Example:
            >>> from trcks.oop import ResultWrapper
            >>> def log_err(e: str) -> tuple[None, ...]:
            ...     print(f"Error logged: {e}")
            ...     print(f"Alert sent: {e}")
            ...     return (None, None)
            ...
            >>> ResultWrapper.construct_failure(
            ...     "critical"
            ... ).tap_failure_to_tuple(log_err)
            Error logged: critical
            Alert sent: critical
            ResultTupleWrapper(core=('success', ('critical', 'critical')))
            >>>
            >>> ResultWrapper.construct_success(
            ...     42
            ... ).tap_failure_to_tuple(log_err)
            ResultTupleWrapper(core=('success', (42,)))
        """
        return ResultTupleWrapper.construct_from_result(self.core).tap_failure_to_tuple(
            f
        )

    def tap_success(
        self, f: Callable[[_S_default_co], object]
    ) -> ResultWrapper[_F_default_co, _S_default_co]:
        """Apply a synchronous side effect to the wrapped [trcks.Success][] object.

        Wrapped [trcks.Failure][] objects are passed on without side effects.

        Args:
            f: The synchronous side effect to be applied.

        Returns:
            A new [trcks.oop.ResultWrapper][] instance
                with the original [trcks.Result][] object,
                allowing for further method chaining.

        Example:
            >>> result_wrapper_1 = ResultWrapper.construct_failure(
            ...     "not found"
            ... ).tap_success(lambda n: print(f"Number: {n}"))
            >>> result_wrapper_1
            ResultWrapper(core=('failure', 'not found'))
            >>> result_wrapper_2 = ResultWrapper.construct_success(42).tap_success(
            ...     lambda n: print(f"Number: {n}")
            ... )
            Number: 42
            >>> result_wrapper_2
            ResultWrapper(core=('success', 42))
        """
        return ResultWrapper(r.tap_success(f)(self.core))

    def tap_success_to_awaitable(
        self, f: Callable[[_S_default_co], Awaitable[object]]
    ) -> AwaitableResultWrapper[_F_default_co, _S_default_co]:
        """Apply an asynchronous side effect to the wrapped [trcks.Success][] object.

        Wrapped [trcks.Failure][] objects are passed on without side effects.

        Args:
            f: The asynchronous side effect to be applied.

        Returns:
            A [trcks.oop.AwaitableResultWrapper][] instance
                with the original [trcks.Result][] object,
                allowing for further method chaining.

        Example:
            >>> import asyncio
            >>> from trcks.oop import ResultWrapper
            >>> async def write_to_disk(s: str) -> None:
            ...     await asyncio.sleep(0.001)
            ...     print(f"Wrote '{s}' to disk.")
            ...
            >>> awaitable_result_wrapper_1 = ResultWrapper.construct_failure(
            ...     "missing text"
            ... ).tap_success_to_awaitable(write_to_disk)
            >>> awaitable_result_wrapper_1
            AwaitableResultWrapper(core=<coroutine object ...>)
            >>> result_1 = asyncio.run(awaitable_result_wrapper_1.core_as_coroutine)
            >>> result_1
            ('failure', 'missing text')
            >>> awaitable_result_wrapper_2 = ResultWrapper.construct_success(
            ...     "Hello, world!"
            ... ).tap_success_to_awaitable(write_to_disk)
            >>> awaitable_result_wrapper_2
            AwaitableResultWrapper(core=<coroutine object ...>)
            >>> result_2 = asyncio.run(awaitable_result_wrapper_2.core_as_coroutine)
            Wrote 'Hello, world!' to disk.
            >>> result_2
            ('success', 'Hello, world!')
        """
        return AwaitableResultWrapper.construct_from_result(
            self.core
        ).tap_success_to_awaitable(f)

    def tap_success_to_awaitable_result(
        self, f: Callable[[_S_default_co], AwaitableResult[_F, object]]
    ) -> AwaitableResultWrapper[_F_default_co | _F, _S_default_co]:
        """Apply an asynchronous side effect with return type [trcks.Result][]
        to the wrapped [trcks.Success][] object.

        Wrapped [trcks.Failure][] objects are passed on without side effects.

        Args:
            f: The asynchronous side effect to be applied.

        Returns:
            A [trcks.oop.AwaitableResultWrapper][] instance with

                - *the original* [trcks.Failure][] if no side effect was applied,
                - *the returned* [trcks.Failure][]
                    if the applied side effect returns a [trcks.Failure][] and
                - *the original* [trcks.Success][]
                    if the applied side effect returns a [trcks.Success][].

        Example:
            >>> import asyncio
            >>> from trcks import Result
            >>> from trcks.oop import ResultWrapper
            >>> async def write_to_disk(s: str, path: str) -> Result[str, None]:
            ...     if path != "output.txt":
            ...         return "failure", "write error"
            ...     await asyncio.sleep(0.001)
            ...     print(f"Wrote '{s}' to file {path}.")
            ...     return "success", None
            ...
            >>> awaitable_result_wrapper_1 = ResultWrapper.construct_failure(
            ...     "missing text"
            ... ).tap_success_to_awaitable_result(
            ...     lambda s: write_to_disk(s, "destination.txt")
            ... )
            >>> awaitable_result_wrapper_1
            AwaitableResultWrapper(core=<coroutine object ...>)
            >>> result_1 = asyncio.run(awaitable_result_wrapper_1.core_as_coroutine)
            >>> result_1
            ('failure', 'missing text')
            >>> awaitable_result_wrapper_2 = ResultWrapper.construct_failure(
            ...     "missing text"
            ... ).tap_success_to_awaitable_result(
            ...     lambda s: write_to_disk(s, "output.txt")
            ... )
            >>> awaitable_result_wrapper_2
            AwaitableResultWrapper(core=<coroutine object ...>)
            >>> result_2 = asyncio.run(awaitable_result_wrapper_2.core_as_coroutine)
            >>> result_2
            ('failure', 'missing text')
            >>> awaitable_result_wrapper_3 = ResultWrapper.construct_success(
            ...     "Hello, world!"
            ... ).tap_success_to_awaitable_result(
            ...     lambda s: write_to_disk(s, "destination.txt")
            ... )
            >>> awaitable_result_wrapper_3
            AwaitableResultWrapper(core=<coroutine object ...>)
            >>> result_3 = asyncio.run(awaitable_result_wrapper_3.core_as_coroutine)
            >>> result_3
            ('failure', 'write error')
            >>> awaitable_result_wrapper_4 = ResultWrapper.construct_success(
            ...     "Hello, world!"
            ... ).tap_success_to_awaitable_result(
            ...     lambda s: write_to_disk(s, "output.txt")
            ... )
            >>> awaitable_result_wrapper_4
            AwaitableResultWrapper(core=<coroutine object ...>)
            >>> result_4 = asyncio.run(awaitable_result_wrapper_4.core_as_coroutine)
            Wrote 'Hello, world!' to file output.txt.
            >>> result_4
            ('success', 'Hello, world!')
        """
        return AwaitableResultWrapper.construct_from_result(
            self.core
        ).tap_success_to_awaitable_result(f)

    def tap_success_to_awaitable_result_tuple(
        self, f: Callable[[_S_default_co], AwaitableResultTuple[_F, object]]
    ) -> AwaitableResultTupleWrapper[_F_default_co | _F, _S_default_co]:
        """Apply an asynchronous side effect with return type
        [trcks.ResultTuple][] to the wrapped [trcks.Success][] object.

        Wrapped [trcks.Failure][] objects are passed on without side effects.

        Args:
            f: The asynchronous side effect to be applied.

        Returns:
            A [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - *the original* [trcks.Failure][] if no side effect was applied,
                - *the returned* [trcks.Failure][]
                    if the applied side effect returns a [trcks.Failure][] and
                - *the original* [trcks.Success][] repeated once per element
                    in the returned [trcks.SuccessTuple][]
                    if the applied side effect returns a [trcks.SuccessTuple][].

        Example:
            >>> import asyncio
            >>> from trcks import AwaitableResultTuple
            >>> from trcks.oop import ResultWrapper
            >>> async def write_twice(
            ...     s: str,
            ... ) -> AwaitableResultTuple[str, None]:
            ...     await asyncio.sleep(0.001)
            ...     print(f"Wrote '{s}' twice.")
            ...     return "success", (None, None)
            ...
            >>> wrapper_1 = (
            ...     ResultWrapper
            ...     .construct_failure("missing text")
            ...     .tap_success_to_awaitable_result_tuple(write_twice)
            ... )
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('failure', 'missing text')
            >>>
            >>> wrapper_2 = (
            ...     ResultWrapper
            ...     .construct_success("Hello, world!")
            ...     .tap_success_to_awaitable_result_tuple(write_twice)
            ... )
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> result_2 = asyncio.run(wrapper_2.core_as_coroutine)
            Wrote 'Hello, world!' twice.
            >>> result_2
            ('success', ('Hello, world!', 'Hello, world!'))
        """
        return AwaitableResultTupleWrapper.construct_from_result(
            self.core
        ).tap_successes_to_awaitable_result_tuple(f)

    def tap_success_to_result(
        self, f: Callable[[_S_default_co], Result[_F, object]]
    ) -> ResultWrapper[_F_default_co | _F, _S_default_co]:
        """Apply a synchronous side effect with return type [trcks.Result][]
        to the wrapped [trcks.Success][] object.

        Wrapped [trcks.Failure][] objects are passed on without side effects.

        Args:
            f: The synchronous side effect to be applied.

        Returns:
            A new [trcks.oop.ResultWrapper][] instance with

                - *the original* [trcks.Failure][] if no side effect was applied,
                - *the returned* [trcks.Failure][]
                    if the applied side effect returns a [trcks.Failure][] and
                - *the original* [trcks.Success][]
                    if the applied side effect returns a [trcks.Success][].
        """
        return ResultWrapper(r.tap_success_to_result(f)(self.core))

    def tap_success_to_result_tuple(
        self, f: Callable[[_S_default_co], ResultTuple[_F, object]]
    ) -> ResultTupleWrapper[_F_default_co | _F, _S_default_co]:
        """Apply a synchronous side effect with return type [trcks.ResultTuple][]
        to the wrapped [trcks.Success][] object.

        Wrapped [trcks.Failure][] objects are passed on without side effects.

        Args:
            f: The synchronous side effect to be applied.

        Returns:
            A [trcks.oop.ResultTupleWrapper][] instance with

                - *the original* [trcks.Failure][] if no side effect was applied,
                - *the returned* [trcks.Failure][]
                    if the applied side effect returns a [trcks.Failure][] and
                - *the original* [trcks.Success][] (wrapped and repeated once
                    per element in the side effect output) if the applied side effect
                    returns [trcks.SuccessTuple][].

        Example:
            >>> from trcks import ResultTuple
            >>> from trcks.oop import ResultWrapper
            >>> def audit(n: int) -> ResultTuple[str, None]:
            ...     if n > 0:
            ...         return "success", (None, None)
            ...     return "failure", "negative"
            ...
            >>> ResultWrapper.construct_failure(
            ...     "oops"
            ... ).tap_success_to_result_tuple(audit)
            ResultTupleWrapper(core=('failure', 'oops'))
            >>>
            >>> ResultWrapper.construct_success(
            ...     7
            ... ).tap_success_to_result_tuple(audit)
            ResultTupleWrapper(core=('success', (7, 7)))
            >>>
            >>> ResultWrapper.construct_success(
            ...     -1
            ... ).tap_success_to_result_tuple(audit)
            ResultTupleWrapper(core=('failure', 'negative'))
        """
        return ResultTupleWrapper.construct_from_result(
            self.core
        ).tap_successes_to_result_tuple(f)

    def tap_success_to_tuple(
        self, f: Callable[[_S_default_co], tuple[object, ...]]
    ) -> ResultTupleWrapper[_F_default_co, _S_default_co]:
        """Apply a synchronous side effect returning a [tuple][]
        to the wrapped [trcks.Success][] object.

        The original success value is repeated once per element
        in the tuple returned by the side effect.

        Wrapped [trcks.Failure][] objects are passed on without side effects.

        Args:
            f: The synchronous side effect to be applied,
                returning a homogeneous [tuple][].

        Returns:
            A [trcks.oop.ResultTupleWrapper][] instance with

                - *the original* [trcks.Failure][] if no side effect was applied, or
                - a [trcks.SuccessTuple][] where the original element is repeated
                    once per element in the tuple returned by the side effect.

        Example:
            >>> from trcks.oop import ResultWrapper
            >>> def log_mult(n: int) -> tuple[None, ...]:
            ...     print(f"v={n}")
            ...     print(f"v={n}")
            ...     return None, None
            ...
            >>> ResultWrapper.construct_failure(
            ...     "error"
            ... ).tap_success_to_tuple(log_mult)
            ResultTupleWrapper(core=('failure', 'error'))
            >>>
            >>> ResultWrapper.construct_success(
            ...     7
            ... ).tap_success_to_tuple(log_mult)
            v=7
            v=7
            ResultTupleWrapper(core=('success', (7, 7)))
        """
        return ResultTupleWrapper.construct_from_result(
            self.core
        ).tap_successes_to_tuple(f)


class ResultTupleWrapper(_ResultWrapper[_F_default_co, tuple[_S_default_co, ...]]):
    """Type-safe and immutable wrapper for [trcks.ResultTuple][] objects.

    The wrapped object can be accessed via the attribute
    `trcks.oop.ResultTupleWrapper.core`.
    The `trcks.oop.ResultTupleWrapper.map*` methods allow method chaining.
    The `trcks.oop.ResultTupleWrapper.tap*` methods allow for side effects.

    Example:
        Map and tap each element inside a success tuple:

        >>> from trcks.oop import ResultTupleWrapper
        >>> def double_integer(n: int) -> int:
        ...     return n * 2
        ...
        >>> def duplicate_integer(n: int) -> tuple[int, int]:
        ...     return n, n
        ...
        >>> def log_integer(n: int) -> None:
        ...     print(f"Received: {n}")
        ...
        >>> result_tuple_wrapper = (
        ...     ResultTupleWrapper
        ...     .construct_successes_from_tuple((1, 2, 3))
        ...     .map_successes(double_integer)
        ...     .tap_successes(log_integer)
        ...     .map_successes_to_tuple(duplicate_integer)
        ... )
        Received: 2
        Received: 4
        Received: 6
        >>> result_tuple_wrapper
        ResultTupleWrapper(core=('success', (2, 2, 4, 4, 6, 6)))
    """

    @staticmethod
    def construct_failure(value: _F) -> ResultTupleWrapper[_F, Never]:
        """Construct and wrap a [trcks.Failure][] object from a value.

        Args:
            value: The value to be wrapped.

        Returns:
            A new [trcks.oop.ResultTupleWrapper][] instance with
                the wrapped [trcks.Failure][] object.

        Example:
            >>> ResultTupleWrapper.construct_failure("not found")
            ResultTupleWrapper(core=('failure', 'not found'))
        """
        return ResultTupleWrapper(rt.construct_failure(value))

    @staticmethod
    def construct_from_result(
        rslt: Result[_F_default, _S_default],
    ) -> ResultTupleWrapper[_F_default, _S_default]:
        """Construct and wrap a [trcks.ResultTuple][] object from a
        [trcks.Result][] object.

        Args:
            rslt: The [trcks.Result][] object to be wrapped.

        Returns:
            A new [trcks.oop.ResultTupleWrapper][] instance with
                the wrapped [trcks.ResultTuple][] object.

        Example:
            >>> from trcks.oop import ResultTupleWrapper
            >>> ResultTupleWrapper.construct_from_result(("success", 7))
            ResultTupleWrapper(core=('success', (7,)))
            >>> ResultTupleWrapper.construct_from_result(("failure", "oops"))
            ResultTupleWrapper(core=('failure', 'oops'))
        """
        return ResultTupleWrapper(rt.construct_from_result(rslt))

    @staticmethod
    def construct_successes(value: _S) -> ResultTupleWrapper[Never, _S]:
        """Construct and wrap a [trcks.SuccessTuple][] object from a value.

        Args:
            value: The value to be wrapped.

        Returns:
            A new [trcks.oop.ResultTupleWrapper][] instance with
                the wrapped [trcks.SuccessTuple][] object.

        Example:
            >>> ResultTupleWrapper.construct_successes(42)
            ResultTupleWrapper(core=('success', (42,)))
        """
        return ResultTupleWrapper(rt.construct_successes(value))

    @staticmethod
    def construct_successes_from_tuple(
        tpl: tuple[_S, ...],
    ) -> ResultTupleWrapper[Never, _S]:
        """Construct and wrap a [trcks.SuccessTuple][] object from a tuple.

        Args:
            tpl: The tuple to be wrapped.

        Returns:
            A new [trcks.oop.ResultTupleWrapper][] instance with
                the wrapped [trcks.SuccessTuple][] object.

        Example:
            >>> ResultTupleWrapper.construct_successes_from_tuple((1, 2))
            ResultTupleWrapper(core=('success', (1, 2)))
        """
        return ResultTupleWrapper(rt.construct_successes_from_tuple(tpl))

    def map_failure(
        self, f: Callable[[_F_default_co], _F]
    ) -> ResultTupleWrapper[_F, _S_default_co]:
        """Apply a synchronous function to the wrapped [trcks.Failure][] object.

        Wrapped [trcks.SuccessTuple][] objects are passed on unchanged.

        Args:
            f: The synchronous function to be applied.

        Returns:
            A new [trcks.oop.ResultTupleWrapper][] instance with

                - the result of the function application if
                    the original [trcks.ResultTuple][] is a failure, or
                - the original [trcks.ResultTuple][] object if it is a success.

        Example:
            >>> from trcks.oop import ResultTupleWrapper
            >>> def _add_prefix(description: str) -> str:
            ...     return f"err: {description}"
            ...
            >>> ResultTupleWrapper.construct_failure("not found").map_failure(
            ...     _add_prefix
            ... )
            ResultTupleWrapper(core=('failure', 'err: not found'))
            >>>
            >>> ResultTupleWrapper.construct_successes_from_tuple(
            ...     (1, 2)
            ... ).map_failure(_add_prefix)
            ResultTupleWrapper(core=('success', (1, 2)))
        """
        return ResultTupleWrapper(rt.map_failure(f)(self.core))

    def map_failure_to_awaitable(
        self, f: Callable[[_F_default_co], Awaitable[_F]]
    ) -> AwaitableResultTupleWrapper[_F, _S_default_co]:
        """Apply an asynchronous function to the wrapped [trcks.Failure][] object.

        Wrapped [trcks.SuccessTuple][] objects are passed on unchanged.

        Args:
            f: The asynchronous function to be applied.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - the result of the function application if
                    the original [trcks.ResultTuple][] is a failure, or
                - the original [trcks.ResultTuple][] if it is a success.

        Example:
            >>> import asyncio
            >>> from trcks.oop import ResultTupleWrapper
            >>> async def prefix_slowly(e: str) -> str:
            ...     await asyncio.sleep(0.001)
            ...     return f"err: {e}"
            ...
            >>> wrapper_1 = ResultTupleWrapper.construct_failure(
            ...     "not found"
            ... ).map_failure_to_awaitable(prefix_slowly)
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('failure', 'err: not found')
            >>>
            >>> wrapper_2 = ResultTupleWrapper.construct_successes_from_tuple(
            ...     (1, 2)
            ... ).map_failure_to_awaitable(prefix_slowly)
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('success', (1, 2))
        """
        return AwaitableResultTupleWrapper.construct_from_result_tuple(
            self.core
        ).map_failure_to_awaitable(f)

    def map_failure_to_awaitable_result_tuple(
        self, f: Callable[[_F_default_co], AwaitableResultTuple[_F, _S]]
    ) -> AwaitableResultTupleWrapper[_F, _S_default_co | _S]:
        """Apply an asynchronous function with return type
        [trcks.ResultTuple][] to the wrapped [trcks.Failure][] object.

        Wrapped [trcks.SuccessTuple][] objects are passed on unchanged.

        Args:
            f: The asynchronous function to be applied.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - the result of the function application if
                    the original [trcks.ResultTuple][] is a failure, or
                - the original [trcks.ResultTuple][] if it is a success.

        Example:
            >>> import asyncio
            >>> from trcks import AwaitableResultTuple
            >>> from trcks.oop import ResultTupleWrapper
            >>> async def recover(
            ...     e: str,
            ... ) -> AwaitableResultTuple[str, int]:
            ...     await asyncio.sleep(0.001)
            ...     if e == "not found":
            ...         return "success", (0, 1)
            ...     return "failure", e
            ...
            >>> wrapper_1 = ResultTupleWrapper.construct_failure(
            ...     "not found"
            ... ).map_failure_to_awaitable_result_tuple(recover)
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('success', (0, 1))
            >>>
            >>> wrapper_2 = ResultTupleWrapper.construct_successes_from_tuple(
            ...     (1, 2)
            ... ).map_failure_to_awaitable_result_tuple(recover)
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('success', (1, 2))
        """
        return AwaitableResultTupleWrapper.construct_from_result_tuple(
            self.core
        ).map_failure_to_awaitable_result_tuple(f)

    def map_failure_to_result(
        self, f: Callable[[_F_default_co], Result[_F, _S]]
    ) -> ResultTupleWrapper[_F, _S_default_co | _S]:
        """Apply a synchronous function with return type [trcks.Result][]
        to the wrapped [trcks.Failure][] object.

        Wrapped [trcks.SuccessTuple][] objects are passed on unchanged.

        Args:
            f: The synchronous function to be applied.

        Returns:
            A new [trcks.oop.ResultTupleWrapper][] instance with

                - the result of the function application if
                    the original [trcks.ResultTuple][] is a failure, or
                - the original [trcks.ResultTuple][] object if it is a success.

        Example:
            >>> from trcks import Result
            >>> from trcks.oop import ResultTupleWrapper
            >>> def _recover_from_not_found(description: str) -> Result[str, int]:
            ...     if description == "not found":
            ...         return "success", 0
            ...     return "failure", description
            ...
            >>> ResultTupleWrapper.construct_failure(
            ...     "not found"
            ... ).map_failure_to_result(_recover_from_not_found)
            ResultTupleWrapper(core=('success', (0,)))
            >>>
            >>> ResultTupleWrapper.construct_failure(
            ...     "not authorized"
            ... ).map_failure_to_result(_recover_from_not_found)
            ResultTupleWrapper(core=('failure', 'not authorized'))
            >>>
            >>> ResultTupleWrapper.construct_successes_from_tuple(
            ...     (1, 2)
            ... ).map_failure_to_result(_recover_from_not_found)
            ResultTupleWrapper(core=('success', (1, 2)))
        """
        mapped_f: Callable[
            [ResultTuple[_F_default_co, _S_default_co]],
            ResultTuple[_F, _S_default_co | _S],
        ] = rt.map_failure_to_result(f)
        return ResultTupleWrapper(mapped_f(self.core))

    def map_failure_to_result_tuple(
        self, f: Callable[[_F_default_co], ResultTuple[_F, _S]]
    ) -> ResultTupleWrapper[_F, _S_default_co | _S]:
        """Apply a synchronous function with return type [trcks.ResultTuple][]
        to the wrapped [trcks.Failure][] object.

        Wrapped [trcks.SuccessTuple][] objects are passed on unchanged.

        Args:
            f: The synchronous function to be applied.

        Returns:
            A new [trcks.oop.ResultTupleWrapper][] instance with

                - the result of the function application if
                    the original [trcks.ResultTuple][] is a failure, or
                - the original [trcks.ResultTuple][] object if it is a success.

        Example:
            >>> from trcks import ResultTuple
            >>> from trcks.oop import ResultTupleWrapper
            >>> def _recover_from_not_found(description: str) -> ResultTuple[str, int]:
            ...     if description == "not found":
            ...         return "success", (0,)
            ...     return "failure", description
            ...
            >>> ResultTupleWrapper.construct_failure(
            ...     "not found"
            ... ).map_failure_to_result_tuple(_recover_from_not_found)
            ResultTupleWrapper(core=('success', (0,)))
            >>>
            >>> ResultTupleWrapper.construct_failure(
            ...     "not authorized"
            ... ).map_failure_to_result_tuple(_recover_from_not_found)
            ResultTupleWrapper(core=('failure', 'not authorized'))
            >>>
            >>> ResultTupleWrapper.construct_successes_from_tuple(
            ...     (1, 2)
            ... ).map_failure_to_result_tuple(_recover_from_not_found)
            ResultTupleWrapper(core=('success', (1, 2)))
        """
        mapped_f: Callable[
            [ResultTuple[_F_default_co, _S_default_co]],
            ResultTuple[_F, _S_default_co | _S],
        ] = rt.map_failure_to_result_tuple(f)
        return ResultTupleWrapper(mapped_f(self.core))

    def map_failure_to_tuple(
        self, f: Callable[[_F_default_co], tuple[_S, ...]]
    ) -> ResultTupleWrapper[Never, _S_default_co | _S]:
        """Apply a synchronous function returning a tuple
        to the wrapped [trcks.Failure][] object.

        Wrapped [trcks.SuccessTuple][] objects are passed on unchanged.

        Args:
            f: The synchronous function to be applied.

        Returns:
            A new [trcks.oop.ResultTupleWrapper][] instance with

                - a [trcks.SuccessTuple][] containing the result of
                    the function application if
                    the original [trcks.ResultTuple][] is a failure, or
                - the original [trcks.ResultTuple][] object if it is a success.

        Example:
            >>> from trcks.oop import ResultTupleWrapper
            >>> def _recover_from_not_found(description: str) -> tuple[int, ...]:
            ...     if description == "not found":
            ...         return (0,)
            ...     return ()
            ...
            >>> ResultTupleWrapper.construct_failure(
            ...     "not found"
            ... ).map_failure_to_tuple(_recover_from_not_found)
            ResultTupleWrapper(core=('success', (0,)))
            >>>
            >>> ResultTupleWrapper.construct_failure(
            ...     "not authorized"
            ... ).map_failure_to_tuple(_recover_from_not_found)
            ResultTupleWrapper(core=('success', ()))
            >>>
            >>> ResultTupleWrapper.construct_successes_from_tuple(
            ...     (1, 2)
            ... ).map_failure_to_tuple(_recover_from_not_found)
            ResultTupleWrapper(core=('success', (1, 2)))
        """
        mapped_f: Callable[
            [ResultTuple[_F_default_co, _S_default_co]],
            ResultTuple[Never, _S_default_co | _S],
        ] = rt.map_failure_to_tuple(f)
        return ResultTupleWrapper(mapped_f(self.core))

    def map_successes(
        self, f: Callable[[_S_default_co], _S]
    ) -> ResultTupleWrapper[_F_default_co, _S]:
        """Apply a synchronous function to each element in the wrapped
        [trcks.SuccessTuple][].

        Wrapped [trcks.Failure][] objects are passed on unchanged.

        Args:
            f: The synchronous function to be applied to each success element.

        Returns:
            A new [trcks.oop.ResultTupleWrapper][] instance with

                - the original [trcks.ResultTuple][] object if it is a failure, or
                - a [trcks.SuccessTuple][] with transformed elements if
                    the original [trcks.ResultTuple][] is a success.

        Example:
            >>> from trcks.oop import ResultTupleWrapper
            >>> def _double_integer(n: int) -> int:
            ...     return n * 2
            ...
            >>> ResultTupleWrapper.construct_successes_from_tuple(
            ...     (1, 2, 3)
            ... ).map_successes(_double_integer)
            ResultTupleWrapper(core=('success', (2, 4, 6)))
            >>>
            >>> ResultTupleWrapper.construct_failure("not found").map_successes(
            ...     _double_integer
            ... )
            ResultTupleWrapper(core=('failure', 'not found'))
        """
        return ResultTupleWrapper(rt.map_successes(f)(self.core))

    def map_successes_to_awaitable(
        self, f: Callable[[_S_default_co], Awaitable[_S]]
    ) -> AwaitableResultTupleWrapper[_F_default_co, _S]:
        """Apply an asynchronous function to each element in the wrapped
        [trcks.SuccessTuple][].

        Wrapped [trcks.Failure][] objects are passed on unchanged.

        Args:
            f: The asynchronous function to be applied to each success element.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - the original [trcks.ResultTuple][] if it is a failure, or
                - an awaitable [trcks.SuccessTuple][] with all transformed
                    elements.

        Example:
            >>> import asyncio
            >>> from trcks.oop import ResultTupleWrapper
            >>> async def double_slowly(n: int) -> int:
            ...     await asyncio.sleep(0.001)
            ...     return n * 2
            ...
            >>> wrapper_1 = ResultTupleWrapper.construct_failure(
            ...     "not found"
            ... ).map_successes_to_awaitable(double_slowly)
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('failure', 'not found')
            >>>
            >>> wrapper_2 = ResultTupleWrapper.construct_successes_from_tuple(
            ...     (1, 2)
            ... ).map_successes_to_awaitable(double_slowly)
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('success', (2, 4))
        """
        return AwaitableResultTupleWrapper.construct_from_result_tuple(
            self.core
        ).map_successes_to_awaitable(f)

    def map_successes_to_awaitable_result(
        self, f: Callable[[_S_default_co], AwaitableResult[_F, _S]]
    ) -> AwaitableResultTupleWrapper[_F_default_co | _F, _S]:
        """Apply an asynchronous function with return type [trcks.Result][]
        to each element in the wrapped [trcks.SuccessTuple][].

        Wrapped [trcks.Failure][] objects are passed on unchanged.

        Args:
            f: The asynchronous function to be applied to each success element.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - the original [trcks.ResultTuple][] if it is a failure, or
                - the first [trcks.Failure][] returned by the function, or
                - an awaitable [trcks.SuccessTuple][] with all transformed
                    elements if the function returns [trcks.Success][] for all.

        Example:
            >>> import asyncio
            >>> from trcks import Result
            >>> from trcks.oop import ResultTupleWrapper
            >>> async def slowly_double_if_positive(n: int) -> Result[str, int]:
            ...     await asyncio.sleep(0.001)
            ...     if n > 0:
            ...         return "success", n * 2
            ...     return "failure", "negative"
            ...
            >>> wrapper_1 = ResultTupleWrapper.construct_failure(
            ...     "not found"
            ... ).map_successes_to_awaitable_result(slowly_double_if_positive)
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('failure', 'not found')
            >>>
            >>> wrapper_2 = ResultTupleWrapper.construct_successes_from_tuple(
            ...     (1, 2)
            ... ).map_successes_to_awaitable_result(slowly_double_if_positive)
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('success', (2, 4))
        """
        return AwaitableResultTupleWrapper.construct_from_result_tuple(
            self.core
        ).map_successes_to_awaitable_result(f)

    def map_successes_to_awaitable_result_tuple(
        self, f: Callable[[_S_default_co], AwaitableResultTuple[_F, _S]]
    ) -> AwaitableResultTupleWrapper[_F_default_co | _F, _S]:
        """Apply an asynchronous function with return type
        [trcks.ResultTuple][] to each element in the wrapped
        [trcks.SuccessTuple][] and flatten.

        Wrapped [trcks.Failure][] objects are passed on unchanged.

        Args:
            f: The asynchronous function to be applied to each success element.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - the original [trcks.ResultTuple][] if it is a failure, or
                - the first [trcks.Failure][] returned by the function, or
                - a flattened awaitable [trcks.SuccessTuple][] if the function
                    returns [trcks.SuccessTuple][] for all elements.

        Example:
            >>> import asyncio
            >>> from trcks import AwaitableResultTuple
            >>> from trcks.oop import ResultTupleWrapper
            >>> async def slowly_expand(
            ...     n: int,
            ... ) -> AwaitableResultTuple[str, int]:
            ...     await asyncio.sleep(0.001)
            ...     if n > 0:
            ...         return "success", (n, -n)
            ...     return "failure", "negative"
            ...
            >>> wrapper_1 = ResultTupleWrapper.construct_failure(
            ...     "not found"
            ... ).map_successes_to_awaitable_result_tuple(slowly_expand)
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('failure', 'not found')
            >>>
            >>> wrapper_2 = ResultTupleWrapper.construct_successes_from_tuple(
            ...     (1, 2)
            ... ).map_successes_to_awaitable_result_tuple(slowly_expand)
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('success', (1, -1, 2, -2))
        """
        return AwaitableResultTupleWrapper.construct_from_result_tuple(
            self.core
        ).map_successes_to_awaitable_result_tuple(f)

    def map_successes_to_result(
        self, f: Callable[[_S_default_co], Result[_F, _S]]
    ) -> ResultTupleWrapper[_F_default_co | _F, _S]:
        """Apply a synchronous function with return type [trcks.Result][]
        to each element in the wrapped [trcks.SuccessTuple][].

        Wrapped [trcks.Failure][] objects are passed on unchanged.

        Args:
            f: The synchronous function to be applied to each success element.

        Returns:
            A new [trcks.oop.ResultTupleWrapper][] instance with

                - the original [trcks.ResultTuple][] object if it is a failure, or
                - the first [trcks.Failure][] returned by the function, or
                - a [trcks.SuccessTuple][] with all transformed elements if
                    the function returns [trcks.Success][] for all elements.

        Example:
            >>> from trcks import Result
            >>> from trcks.oop import ResultTupleWrapper
            >>> def double_if_positive(n: int) -> Result[str, int]:
            ...     if n > 0:
            ...         return "success", n * 2
            ...     return "failure", "not positive"
            ...
            >>> ResultTupleWrapper.construct_successes_from_tuple(
            ...     (1, 2)
            ... ).map_successes_to_result(double_if_positive)
            ResultTupleWrapper(core=('success', (2, 4)))
            >>>
            >>> ResultTupleWrapper.construct_successes_from_tuple(
            ...     (1, -1, 2)
            ... ).map_successes_to_result(double_if_positive)
            ResultTupleWrapper(core=('failure', 'not positive'))
            >>>
            >>> ResultTupleWrapper.construct_failure(
            ...     "oops"
            ... ).map_successes_to_result(double_if_positive)
            ResultTupleWrapper(core=('failure', 'oops'))
        """
        mapped_f: Callable[
            [ResultTuple[_F_default_co, _S_default_co]],
            ResultTuple[_F_default_co | _F, _S],
        ] = rt.map_successes_to_result(f)
        return ResultTupleWrapper(mapped_f(self.core))

    def map_successes_to_result_tuple(
        self, f: Callable[[_S_default_co], ResultTuple[_F, _S]]
    ) -> ResultTupleWrapper[_F_default_co | _F, _S]:
        """Apply a synchronous function with return type [trcks.ResultTuple][]
        to each element in the wrapped [trcks.SuccessTuple][] and flatten.

        Wrapped [trcks.Failure][] objects are passed on unchanged.

        Args:
            f: The synchronous function to be applied to each success element.

        Returns:
            A new [trcks.oop.ResultTupleWrapper][] instance with

                - the original [trcks.ResultTuple][] object if it is a failure, or
                - the first [trcks.Failure][] returned by the function, or
                - a flattened [trcks.SuccessTuple][] if the function returns
                    [trcks.SuccessTuple][] for all elements.

        Example:
            >>> from trcks import ResultTuple
            >>> from trcks.oop import ResultTupleWrapper
            >>> def duplicate_if_positive(n: int) -> ResultTuple[str, int]:
            ...     if n > 0:
            ...         return "success", (n, n)
            ...     return "failure", "not positive"
            ...
            >>> ResultTupleWrapper.construct_successes_from_tuple(
            ...     (1, 2)
            ... ).map_successes_to_result_tuple(duplicate_if_positive)
            ResultTupleWrapper(core=('success', (1, 1, 2, 2)))
            >>>
            >>> ResultTupleWrapper.construct_successes_from_tuple(
            ...     (1, -1, 2)
            ... ).map_successes_to_result_tuple(duplicate_if_positive)
            ResultTupleWrapper(core=('failure', 'not positive'))
            >>>
            >>> ResultTupleWrapper.construct_failure(
            ...     "oops"
            ... ).map_successes_to_result_tuple(duplicate_if_positive)
            ResultTupleWrapper(core=('failure', 'oops'))
        """
        mapped_f: Callable[
            [ResultTuple[_F_default_co, _S_default_co]],
            ResultTuple[_F_default_co | _F, _S],
        ] = rt.map_successes_to_result_tuple(f)
        return ResultTupleWrapper(mapped_f(self.core))

    def map_successes_to_tuple(
        self, f: Callable[[_S_default_co], tuple[_S, ...]]
    ) -> ResultTupleWrapper[_F_default_co, _S]:
        """Apply a synchronous function returning a tuple
        to each element in the wrapped [trcks.SuccessTuple][] and flatten.

        Wrapped [trcks.Failure][] objects are passed on unchanged.

        Args:
            f: The synchronous function to be applied to each success element.

        Returns:
            A new [trcks.oop.ResultTupleWrapper][] instance with

                - the original [trcks.ResultTuple][] object if it is a failure, or
                - a flattened [trcks.SuccessTuple][] if
                    the original [trcks.ResultTuple][] is a success.

        Example:
            >>> from trcks.oop import ResultTupleWrapper
            >>> def _duplicate_integer(n: int) -> tuple[int, int]:
            ...     return n, n
            ...
            >>> ResultTupleWrapper.construct_successes_from_tuple(
            ...     (1, 2)
            ... ).map_successes_to_tuple(_duplicate_integer)
            ResultTupleWrapper(core=('success', (1, 1, 2, 2)))
            >>>
            >>> ResultTupleWrapper.construct_failure(
            ...     "not found"
            ... ).map_successes_to_tuple(_duplicate_integer)
            ResultTupleWrapper(core=('failure', 'not found'))
        """
        return ResultTupleWrapper(rt.map_successes_to_tuple(f)(self.core))

    def tap_failure(
        self, f: Callable[[_F_default_co], object]
    ) -> ResultTupleWrapper[_F_default_co, _S_default_co]:
        """Apply a synchronous side effect to the wrapped [trcks.Failure][] object.

        Wrapped [trcks.SuccessTuple][] objects are passed on without side effects.

        Args:
            f: The synchronous side effect to be applied.

        Returns:
            A new [trcks.oop.ResultTupleWrapper][] instance
                with the original [trcks.ResultTuple][] object,
                allowing for further method chaining.

        Example:
            >>> from trcks.oop import ResultTupleWrapper
            >>> def _log_error(description: str) -> None:
            ...     print(f"Error: {description}")
            ...
            >>> result_tuple_wrapper_1 = ResultTupleWrapper.construct_failure(
            ...     "oops"
            ... ).tap_failure(_log_error)
            Error: oops
            >>> result_tuple_wrapper_1
            ResultTupleWrapper(core=('failure', 'oops'))
            >>> result_tuple_wrapper_2 = (
            ...     ResultTupleWrapper.construct_successes(1).tap_failure(
            ...         _log_error
            ...     )
            ... )
            >>> result_tuple_wrapper_2
            ResultTupleWrapper(core=('success', (1,)))
        """
        return ResultTupleWrapper(rt.tap_failure(f)(self.core))

    def tap_failure_to_awaitable(
        self, f: Callable[[_F_default_co], Awaitable[object]]
    ) -> AwaitableResultTupleWrapper[_F_default_co, _S_default_co]:
        """Apply an asynchronous side effect to the wrapped
        [trcks.Failure][] object.

        Wrapped [trcks.SuccessTuple][] objects are passed on without side
        effects.

        Args:
            f: The asynchronous side effect to be applied.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with
                the original [trcks.ResultTuple][] object.

        Example:
            >>> import asyncio
            >>> from trcks.oop import ResultTupleWrapper
            >>> async def log_slowly(e: str) -> None:
            ...     await asyncio.sleep(0.001)
            ...     print(f"Error: {e}")
            ...
            >>> wrapper_1 = ResultTupleWrapper.construct_failure(
            ...     "oops"
            ... ).tap_failure_to_awaitable(log_slowly)
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> result_1 = asyncio.run(wrapper_1.core_as_coroutine)
            Error: oops
            >>> result_1
            ('failure', 'oops')
            >>>
            >>> wrapper_2 = ResultTupleWrapper.construct_successes(
            ...     1
            ... ).tap_failure_to_awaitable(log_slowly)
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('success', (1,))
        """
        return AwaitableResultTupleWrapper.construct_from_result_tuple(
            self.core
        ).tap_failure_to_awaitable(f)

    def tap_failure_to_awaitable_result(
        self, f: Callable[[_F_default_co], AwaitableResult[object, _S]]
    ) -> AwaitableResultTupleWrapper[_F_default_co, _S_default_co | _S]:
        """Apply an asynchronous side effect with return type [trcks.Result][]
        to the wrapped [trcks.Failure][] object.

        Wrapped [trcks.SuccessTuple][] objects are passed on without side
        effects.

        Args:
            f: The asynchronous side effect to be applied.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - *the original* [trcks.Failure][]
                    if the applied side effect returns a [trcks.Failure][],
                - *the returned* [trcks.Success][] (wrapped as a tuple)
                    if the applied side effect returns a [trcks.Success][] and
                - *the original* [trcks.SuccessTuple][]
                    if no side effect was applied.

        Example:
            >>> import asyncio
            >>> from trcks import Result
            >>> from trcks.oop import ResultTupleWrapper
            >>> async def recover(e: str) -> Result[object, int]:
            ...     await asyncio.sleep(0.001)
            ...     if e == "not found":
            ...         return "success", 0
            ...     return "failure", e
            ...
            >>> wrapper_1 = ResultTupleWrapper.construct_failure(
            ...     "not found"
            ... ).tap_failure_to_awaitable_result(recover)
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('success', (0,))
            >>>
            >>> wrapper_2 = ResultTupleWrapper.construct_successes(
            ...     1
            ... ).tap_failure_to_awaitable_result(recover)
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('success', (1,))
        """
        return AwaitableResultTupleWrapper.construct_from_result_tuple(
            self.core
        ).tap_failure_to_awaitable_result(f)

    def tap_failure_to_awaitable_result_tuple(
        self, f: Callable[[_F_default_co], AwaitableResultTuple[object, _S]]
    ) -> AwaitableResultTupleWrapper[_F_default_co, _S_default_co | _S]:
        """Apply an asynchronous side effect with return type
        [trcks.ResultTuple][] to the wrapped [trcks.Failure][] object.

        Wrapped [trcks.SuccessTuple][] objects are passed on without side
        effects.

        Args:
            f: The asynchronous side effect to be applied.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - *the original* [trcks.Failure][]
                    if the applied side effect returns a [trcks.Failure][],
                - *the returned* [trcks.SuccessTuple][]
                    if the applied side effect returns a [trcks.SuccessTuple][]
                    and
                - *the original* [trcks.SuccessTuple][]
                    if no side effect was applied.

        Example:
            >>> import asyncio
            >>> from trcks import AwaitableResultTuple
            >>> from trcks.oop import ResultTupleWrapper
            >>> async def recover(
            ...     e: str,
            ... ) -> AwaitableResultTuple[object, int]:
            ...     await asyncio.sleep(0.001)
            ...     if e == "not found":
            ...         return "success", (0, 1)
            ...     return "failure", e
            ...
            >>> wrapper_1 = ResultTupleWrapper.construct_failure(
            ...     "not found"
            ... ).tap_failure_to_awaitable_result_tuple(recover)
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('success', (0, 1))
            >>>
            >>> wrapper_2 = ResultTupleWrapper.construct_successes(
            ...     1
            ... ).tap_failure_to_awaitable_result_tuple(recover)
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('success', (1,))
        """
        return AwaitableResultTupleWrapper.construct_from_result_tuple(
            self.core
        ).tap_failure_to_awaitable_result_tuple(f)

    def tap_failure_to_result(
        self, f: Callable[[_F_default_co], Result[object, _S]]
    ) -> ResultTupleWrapper[_F_default_co, _S_default_co | _S]:
        """Apply a synchronous side effect with return type [trcks.Result][]
        to the wrapped [trcks.Failure][] object.

        Wrapped [trcks.SuccessTuple][] objects are passed on without side effects.

        Args:
            f: The synchronous side effect to be applied.

        Returns:
            A new [trcks.oop.ResultTupleWrapper][] instance with

                - *the original* [trcks.Failure][]
                    if the applied side effect returns a [trcks.Failure][],
                - *the returned* [trcks.Success][] (wrapped as a tuple)
                    if the applied side effect returns a [trcks.Success][] and
                - *the original* [trcks.SuccessTuple][]
                    if no side effect was applied.

        Example:
            >>> from trcks import Result
            >>> from trcks.oop import ResultTupleWrapper
            >>> def recover(e: str) -> Result[None, int]:
            ...     if e == "not found":
            ...         return "success", 42
            ...     return "failure", None
            ...
            >>> ResultTupleWrapper.construct_failure(
            ...     "not found"
            ... ).tap_failure_to_result(recover)
            ResultTupleWrapper(core=('success', (42,)))
            >>>
            >>> ResultTupleWrapper.construct_failure(
            ...     "fatal"
            ... ).tap_failure_to_result(recover)
            ResultTupleWrapper(core=('failure', 'fatal'))
            >>>
            >>> ResultTupleWrapper.construct_successes_from_tuple(
            ...     (1, 2)
            ... ).tap_failure_to_result(recover)
            ResultTupleWrapper(core=('success', (1, 2)))
        """
        tapped_f: Callable[
            [ResultTuple[_F_default_co, _S_default_co]],
            ResultTuple[_F_default_co, _S_default_co | _S],
        ] = rt.tap_failure_to_result(f)
        return ResultTupleWrapper(tapped_f(self.core))

    def tap_failure_to_result_tuple(
        self, f: Callable[[_F_default_co], ResultTuple[object, _S]]
    ) -> ResultTupleWrapper[_F_default_co, _S_default_co | _S]:
        """Apply a synchronous side effect with return type [trcks.ResultTuple][]
        to the wrapped [trcks.Failure][] object.

        Wrapped [trcks.SuccessTuple][] objects are passed on without side effects.

        Args:
            f: The synchronous side effect to be applied.

        Returns:
            A new [trcks.oop.ResultTupleWrapper][] instance with

                - *the original* [trcks.Failure][]
                    if the applied side effect returns a [trcks.Failure][],
                - *the returned* [trcks.SuccessTuple][]
                    if the applied side effect returns a [trcks.SuccessTuple][] and
                - *the original* [trcks.SuccessTuple][]
                    if no side effect was applied.

        Example:
            >>> from trcks import ResultTuple
            >>> from trcks.oop import ResultTupleWrapper
            >>> def recover(e: str) -> ResultTuple[None, int]:
            ...     if e == "not found":
            ...         return "success", (42,)
            ...     return "failure", None
            ...
            >>> ResultTupleWrapper.construct_failure(
            ...     "not found"
            ... ).tap_failure_to_result_tuple(recover)
            ResultTupleWrapper(core=('success', (42,)))
            >>>
            >>> ResultTupleWrapper.construct_failure(
            ...     "fatal"
            ... ).tap_failure_to_result_tuple(recover)
            ResultTupleWrapper(core=('failure', 'fatal'))
            >>>
            >>> ResultTupleWrapper.construct_successes_from_tuple(
            ...     (1, 2)
            ... ).tap_failure_to_result_tuple(recover)
            ResultTupleWrapper(core=('success', (1, 2)))
        """
        tapped_f: Callable[
            [ResultTuple[_F_default_co, _S_default_co]],
            ResultTuple[_F_default_co, _S_default_co | _S],
        ] = rt.tap_failure_to_result_tuple(f)
        return ResultTupleWrapper(tapped_f(self.core))

    def tap_failure_to_tuple(
        self, f: Callable[[_F_default_co], tuple[object, ...]]
    ) -> ResultTupleWrapper[Never, _F_default_co | _S_default_co]:
        """Apply a synchronous side effect returning a tuple
        to the wrapped [trcks.Failure][] object.

        The failure is converted to a [trcks.SuccessTuple][] where
        the original failure value is repeated once per element in
        the tuple returned by the side effect.

        Wrapped [trcks.SuccessTuple][] objects are passed on without side effects.

        Args:
            f: The synchronous side effect to be applied.

        Returns:
            A new [trcks.oop.ResultTupleWrapper][] instance with

                - a [trcks.SuccessTuple][] containing the original failure
                    repeated once per element
                    in the tuple returned by the side effect
                    if the original [trcks.ResultTuple][] is a failure, or
                - the original [trcks.SuccessTuple][] if no side effect was applied.

        Example:
            >>> from trcks.oop import ResultTupleWrapper
            >>> def _log_and_alert(description: str) -> tuple[None, None]:
            ...     return (
            ...         print(f"Error logged: {description}"),
            ...         print(f"Alert sent: {description}"),
            ...     )
            ...
            >>> ResultTupleWrapper.construct_failure(
            ...     "critical"
            ... ).tap_failure_to_tuple(_log_and_alert)
            Error logged: critical
            Alert sent: critical
            ResultTupleWrapper(core=('success', ('critical', 'critical')))
            >>>
            >>> ResultTupleWrapper.construct_successes_from_tuple(
            ...     (1, 2)
            ... ).tap_failure_to_tuple(_log_and_alert)
            ResultTupleWrapper(core=('success', (1, 2)))
        """
        tapped_f: Callable[
            [ResultTuple[_F_default_co, _S_default_co]],
            ResultTuple[Never, _F_default_co | _S_default_co],
        ] = rt.tap_failure_to_tuple(f)
        return ResultTupleWrapper(tapped_f(self.core))

    def tap_successes(
        self, f: Callable[[_S_default_co], object]
    ) -> ResultTupleWrapper[_F_default_co, _S_default_co]:
        """Apply a synchronous side effect to each element in the wrapped
        [trcks.SuccessTuple][].

        Wrapped [trcks.Failure][] objects are passed on without side effects.

        Args:
            f: The synchronous side effect to be applied to each success element.

        Returns:
            A new [trcks.oop.ResultTupleWrapper][] instance
                with the original [trcks.ResultTuple][] object,
                allowing for further method chaining.

        Example:
            >>> from trcks.oop import ResultTupleWrapper
            >>> def _log_integer(n: int) -> None:
            ...     print(f"Received: {n}")
            ...
            >>> result_tuple_wrapper_1 = (
            ...     ResultTupleWrapper.construct_successes_from_tuple((1, 2))
            ...     .tap_successes(_log_integer)
            ... )
            Received: 1
            Received: 2
            >>> result_tuple_wrapper_1
            ResultTupleWrapper(core=('success', (1, 2)))
            >>> result_tuple_wrapper_2 = ResultTupleWrapper.construct_failure(
            ...     "oops"
            ... ).tap_successes(_log_integer)
            >>> result_tuple_wrapper_2
            ResultTupleWrapper(core=('failure', 'oops'))
        """
        return ResultTupleWrapper(rt.tap_successes(f)(self.core))

    def tap_successes_to_awaitable(
        self, f: Callable[[_S_default_co], Awaitable[object]]
    ) -> AwaitableResultTupleWrapper[_F_default_co, _S_default_co]:
        """Apply an asynchronous side effect to each element in the wrapped
        [trcks.SuccessTuple][].

        Wrapped [trcks.Failure][] objects are passed on without side effects.

        Args:
            f: The asynchronous side effect to be applied to each success element.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with
                the original [trcks.ResultTuple][] object.

        Example:
            >>> import asyncio
            >>> from trcks.oop import ResultTupleWrapper
            >>> async def print_slowly(n: int) -> None:
            ...     await asyncio.sleep(0.001)
            ...     print(f"Value: {n}")
            ...
            >>> wrapper_1 = ResultTupleWrapper.construct_failure(
            ...     "oops"
            ... ).tap_successes_to_awaitable(print_slowly)
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('failure', 'oops')
            >>>
            >>> wrapper_2 = ResultTupleWrapper.construct_successes_from_tuple(
            ...     (1, 2)
            ... ).tap_successes_to_awaitable(print_slowly)
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> result_2 = asyncio.run(wrapper_2.core_as_coroutine)
            Value: 1
            Value: 2
            >>> result_2
            ('success', (1, 2))
        """
        return AwaitableResultTupleWrapper.construct_from_result_tuple(
            self.core
        ).tap_successes_to_awaitable(f)

    def tap_successes_to_awaitable_result(
        self, f: Callable[[_S_default_co], AwaitableResult[_F, object]]
    ) -> AwaitableResultTupleWrapper[_F_default_co | _F, _S_default_co]:
        """Apply an asynchronous side effect with return type [trcks.Result][]
        to each element in the wrapped [trcks.SuccessTuple][].

        Wrapped [trcks.Failure][] objects are passed on without side effects.

        Args:
            f: The asynchronous side effect to be applied to each success element.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - *the original* [trcks.Failure][] if no side effect was applied,
                - *the returned* [trcks.Failure][]
                    if the applied side effect returns a [trcks.Failure][] and
                - *the original* [trcks.SuccessTuple][]
                    if the applied side effect returns [trcks.Success][] for all.

        Example:
            >>> import asyncio
            >>> from trcks import Result
            >>> from trcks.oop import ResultTupleWrapper
            >>> async def slowly_check_if_positive(n: int) -> Result[str, None]:
            ...     await asyncio.sleep(0.001)
            ...     if n > 0:
            ...         return "success", None
            ...     return "failure", "negative"
            ...
            >>> wrapper_1 = ResultTupleWrapper.construct_failure(
            ...     "oops"
            ... ).tap_successes_to_awaitable_result(slowly_check_if_positive)
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('failure', 'oops')
            >>>
            >>> wrapper_2 = ResultTupleWrapper.construct_successes_from_tuple(
            ...     (1, 2)
            ... ).tap_successes_to_awaitable_result(slowly_check_if_positive)
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('success', (1, 2))
        """
        return AwaitableResultTupleWrapper.construct_from_result_tuple(
            self.core
        ).tap_successes_to_awaitable_result(f)

    def tap_successes_to_awaitable_result_tuple(
        self, f: Callable[[_S_default_co], AwaitableResultTuple[_F, object]]
    ) -> AwaitableResultTupleWrapper[_F_default_co | _F, _S_default_co]:
        """Apply an asynchronous side effect with return type
        [trcks.ResultTuple][] to each element in the wrapped
        [trcks.SuccessTuple][].

        Wrapped [trcks.Failure][] objects are passed on without side effects.

        Args:
            f: The asynchronous side effect to be applied to each success element.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - *the original* [trcks.Failure][] if no side effect was applied,
                - *the returned* [trcks.Failure][]
                    if the applied side effect returns a [trcks.Failure][] and
                - *the original* [trcks.SuccessTuple][] (with each element
                    repeated per element in the side effect output)
                    if the applied side effect returns [trcks.SuccessTuple][]
                    for all elements.

        Example:
            >>> import asyncio
            >>> from trcks import AwaitableResultTuple
            >>> from trcks.oop import ResultTupleWrapper
            >>> async def audit(
            ...     n: int,
            ... ) -> AwaitableResultTuple[str, None]:
            ...     await asyncio.sleep(0.001)
            ...     if n > 0:
            ...         return "success", (None, None)
            ...     return "failure", "negative"
            ...
            >>> wrapper_1 = ResultTupleWrapper.construct_failure(
            ...     "oops"
            ... ).tap_successes_to_awaitable_result_tuple(audit)
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('failure', 'oops')
            >>>
            >>> wrapper_2 = ResultTupleWrapper.construct_successes_from_tuple(
            ...     (1, 2)
            ... ).tap_successes_to_awaitable_result_tuple(audit)
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('success', (1, 1, 2, 2))
        """
        return AwaitableResultTupleWrapper.construct_from_result_tuple(
            self.core
        ).tap_successes_to_awaitable_result_tuple(f)

    def tap_successes_to_result(
        self, f: Callable[[_S_default_co], Result[_F, object]]
    ) -> ResultTupleWrapper[_F_default_co | _F, _S_default_co]:
        """Apply a synchronous side effect with return type [trcks.Result][]
        to each element in the wrapped [trcks.SuccessTuple][].

        Wrapped [trcks.Failure][] objects are passed on without side effects.

        Args:
            f: The synchronous side effect to be applied to each success element.

        Returns:
            A new [trcks.oop.ResultTupleWrapper][] instance with

                - *the original* [trcks.Failure][] if no side effect was applied,
                - *the returned* [trcks.Failure][]
                    if the applied side effect returns a [trcks.Failure][] and
                - *the original* [trcks.SuccessTuple][]
                    if the applied side effect returns [trcks.Success][]
                    for all elements.

        Example:
            >>> from trcks import Result
            >>> from trcks.oop import ResultTupleWrapper
            >>> def _validate_positive(n: int) -> Result[str, None]:
            ...     if n > 0:
            ...         return "success", None
            ...     return "failure", "not positive"
            ...
            >>> ResultTupleWrapper.construct_successes_from_tuple(
            ...     (1, 2)
            ... ).tap_successes_to_result(_validate_positive)
            ResultTupleWrapper(core=('success', (1, 2)))
            >>>
            >>> ResultTupleWrapper.construct_successes_from_tuple(
            ...     (1, -1, 2)
            ... ).tap_successes_to_result(_validate_positive)
            ResultTupleWrapper(core=('failure', 'not positive'))
            >>>
            >>> ResultTupleWrapper.construct_failure(
            ...     "oops"
            ... ).tap_successes_to_result(_validate_positive)
            ResultTupleWrapper(core=('failure', 'oops'))
        """
        return ResultTupleWrapper(rt.tap_successes_to_result(f)(self.core))

    def tap_successes_to_result_tuple(
        self, f: Callable[[_S_default_co], ResultTuple[_F, object]]
    ) -> ResultTupleWrapper[_F_default_co | _F, _S_default_co]:
        """Apply a synchronous side effect with return type [trcks.ResultTuple][]
        to each element in the wrapped [trcks.SuccessTuple][].

        Wrapped [trcks.Failure][] objects are passed on without side effects.

        Args:
            f: The synchronous side effect to be applied to each success element.

        Returns:
            A new [trcks.oop.ResultTupleWrapper][] instance with

                - *the original* [trcks.Failure][] if no side effect was applied,
                - *the returned* [trcks.Failure][]
                    if the applied side effect returns a [trcks.Failure][] and
                - *the original* [trcks.SuccessTuple][] element repeated once
                    per element in the side effect output if the applied side effect
                    returns [trcks.SuccessTuple][] for all elements.

        Example:
            >>> from trcks import ResultTuple
            >>> from trcks.oop import ResultTupleWrapper
            >>> def _validate_positive_twice(n: int) -> ResultTuple[str, None]:
            ...     if n > 0:
            ...         return "success", (None, None)
            ...     return "failure", "not positive"
            ...
            >>> ResultTupleWrapper.construct_successes(
            ...     7
            ... ).tap_successes_to_result_tuple(_validate_positive_twice)
            ResultTupleWrapper(core=('success', (7, 7)))
            >>>
            >>> ResultTupleWrapper.construct_successes_from_tuple(
            ...     (1, -1)
            ... ).tap_successes_to_result_tuple(_validate_positive_twice)
            ResultTupleWrapper(core=('failure', 'not positive'))
        """
        return ResultTupleWrapper(rt.tap_successes_to_result_tuple(f)(self.core))

    def tap_successes_to_tuple(
        self, f: Callable[[_S_default_co], tuple[object, ...]]
    ) -> ResultTupleWrapper[_F_default_co, _S_default_co]:
        """Apply a synchronous side effect returning a tuple
        to each element in the wrapped [trcks.SuccessTuple][].

        The original success elements are repeated once per element
        in the tuple returned by the side effect.

        Wrapped [trcks.Failure][] objects are passed on without side effects.

        Args:
            f: The synchronous side effect to be applied to each success element.

        Returns:
            A new [trcks.oop.ResultTupleWrapper][] instance with

                - the original [trcks.Failure][] if no side effect was applied, or
                - a [trcks.SuccessTuple][] where each original element is repeated
                    once per element in the tuple returned by the side effect.

        Example:
            >>> from trcks.oop import ResultTupleWrapper
            >>> def _log_twice(n: int) -> tuple[None, None]:
            ...     return print(f"Received: {n}"), print(f"Received: {n}")
            ...
            >>> ResultTupleWrapper.construct_successes(7).tap_successes_to_tuple(
            ...     _log_twice
            ... )
            Received: 7
            Received: 7
            ResultTupleWrapper(core=('success', (7, 7)))
        """
        return ResultTupleWrapper(rt.tap_successes_to_tuple(f)(self.core))


class TupleWrapper(_Wrapper[tuple[_T_co, ...]]):
    """Type-safe and immutable wrapper for homogeneous [tuple][] objects.

    The wrapped homogeneous [tuple][] can be accessed
    via the attribute `trcks.oop.TupleWrapper.core`.
    The `trcks.oop.TupleWrapper.map*` methods allow method chaining.
    The `trcks.oop.TupleWrapper.tap*` methods allow for side effects
    without changing the wrapped tuple.

    Example:
        Create and process a homogeneous [tuple][]:

        >>> from trcks.oop import TupleWrapper
        >>> def double_integer(n: int) -> int:
        ...     return n * 2
        ...
        >>> def log_integer(n: int) -> None:
        ...     print(f"Received: {n}")
        ...
        >>> tuple_wrapper: TupleWrapper[int] = (
        ...     TupleWrapper
        ...     .construct_from_tuple((1, 2, 3))
        ...     .map(double_integer)
        ...     .tap(log_integer)
        ... )
        Received: 2
        Received: 4
        Received: 6
        >>> tuple_wrapper
        TupleWrapper(core=(2, 4, 6))

        Map each element to a homogeneous tuple and flatten the result:

        >>> from trcks.oop import TupleWrapper
        >>> def duplicate_integer(n: int) -> tuple[int, int]:
        ...     return n, n
        ...
        >>> tuple_wrapper: TupleWrapper[int] = (
        ...     TupleWrapper
        ...     .construct_from_tuple((1, 2, 3))
        ...     .map_to_tuple(duplicate_integer)
        ... )
        >>> tuple_wrapper
        TupleWrapper(core=(1, 1, 2, 2, 3, 3))
    """

    @staticmethod
    def construct(value: _T) -> TupleWrapper[_T]:
        """Construct and wrap a [tuple][] from a single value.

        Args:
            value: The value to be wrapped in a [tuple][].

        Returns:
            A new [trcks.oop.TupleWrapper][] instance with
                a [tuple][] containing the single value.

        Example:
            >>> from trcks.oop import TupleWrapper
            >>> tuple_wrapper: TupleWrapper[int] = TupleWrapper.construct(42)
            >>> tuple_wrapper
            TupleWrapper(core=(42,))
        """
        return TupleWrapper(t.construct(value))

    @staticmethod
    def construct_from_tuple(tpl: tuple[_T, ...]) -> TupleWrapper[_T]:
        """Wrap a homogeneous [tuple][] object.

        Args:
            tpl: The homogeneous [tuple][] to be wrapped.

        Returns:
            A new [trcks.oop.TupleWrapper][] instance with
                the wrapped homogeneous [tuple][].

        Example:
            >>> from trcks.oop import TupleWrapper
            >>> tuple_wrapper: TupleWrapper[int] = TupleWrapper.construct_from_tuple(
            ...     (1, 2, 3)
            ... )
            >>> tuple_wrapper
            TupleWrapper(core=(1, 2, 3))
        """
        return TupleWrapper(tpl)

    def map(self, f: Callable[[_T_co], _T]) -> TupleWrapper[_T]:
        """Apply a synchronous function to each element in
        the wrapped homogeneous [tuple][].

        Args:
            f: The synchronous function to be applied to each element.

        Returns:
            A new [trcks.oop.TupleWrapper][] instance with a homogeneous [tuple][]
                containing the results of applying the function to each element.

        Example:
            >>> from trcks.oop import TupleWrapper
            >>> def double_integer(n: int) -> int:
            ...     return n * 2
            ...
            >>> tuple_wrapper: TupleWrapper[int] = (
            ...     TupleWrapper
            ...     .construct_from_tuple((1, 2, 3))
            ...     .map(double_integer)
            ... )
            >>> tuple_wrapper
            TupleWrapper(core=(2, 4, 6))
        """
        return TupleWrapper(t.map_(f)(self.core))

    def map_to_awaitable(
        self, f: Callable[[_T_co], Awaitable[_T]]
    ) -> AwaitableTupleWrapper[_T]:
        """Apply an asynchronous function to each element in the wrapped
        homogeneous [tuple][].

        Args:
            f: The asynchronous function to be applied to each element.

        Returns:
            An [trcks.oop.AwaitableTupleWrapper][] instance with
                an awaitable homogeneous [tuple][] containing
                the results of applying the function to each element.

        Example:
            >>> import asyncio
            >>> from trcks.oop import AwaitableTupleWrapper, TupleWrapper
            >>> async def slowly_add_one(n: int) -> int:
            ...     await asyncio.sleep(0.001)
            ...     return n + 1
            ...
            >>> awaitable_tuple_wrapper: AwaitableTupleWrapper[int] = (
            ...     TupleWrapper
            ...     .construct_from_tuple((1, 2, 3))
            ...     .map_to_awaitable(slowly_add_one)
            ... )
            >>> awaitable_tuple_wrapper
            AwaitableTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_tuple_wrapper.core_as_coroutine)
            (2, 3, 4)
        """
        return AwaitableTupleWrapper.construct_from_tuple(self.core).map_to_awaitable(f)

    def map_to_awaitable_result(
        self, f: Callable[[_T_co], AwaitableResult[_F, _S]]
    ) -> AwaitableResultTupleWrapper[_F, _S]:
        """Apply an asynchronous function with return type [trcks.Result][]
        to each element in the wrapped homogeneous [tuple][].

        Wrapped objects short-circuit on the first [trcks.Failure][].

        Args:
            f: The asynchronous function to be applied to each element.

        Returns:
            An [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - the first [trcks.Failure][] returned by the function, or
                - a [trcks.SuccessTuple][] if the function returns [trcks.Success][]
                    for all elements.

        Example:
            >>> import asyncio
            >>> from trcks import Result
            >>> from trcks.oop import AwaitableResultTupleWrapper, TupleWrapper
            >>> async def slowly_double_if_positive(n: int) -> Result[str, int]:
            ...     await asyncio.sleep(0.001)
            ...     if n > 0:
            ...         return "success", n * 2
            ...     return "failure", "negative"
            ...
            >>> awaitable_result_tuple_wrapper_1: AwaitableResultTupleWrapper[
            ...     str, int
            ... ] = (
            ...     TupleWrapper
            ...     .construct_from_tuple((1, 2))
            ...     .map_to_awaitable_result(slowly_double_if_positive)
            ... )
            >>> awaitable_result_tuple_wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_result_tuple_wrapper_1.core_as_coroutine)
            ('success', (2, 4))
            >>>
            >>> awaitable_result_tuple_wrapper_2: AwaitableResultTupleWrapper[
            ...     str, int
            ... ] = (
            ...     TupleWrapper
            ...     .construct_from_tuple((1, -1, 2))
            ...     .map_to_awaitable_result(slowly_double_if_positive)
            ... )
            >>> awaitable_result_tuple_wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_result_tuple_wrapper_2.core_as_coroutine)
            ('failure', 'negative')
        """
        return AwaitableResultTupleWrapper.construct_successes_from_tuple(
            self.core
        ).map_successes_to_awaitable_result(f)

    def map_to_awaitable_result_tuple(
        self, f: Callable[[_T_co], AwaitableResultTuple[_F, _S]]
    ) -> AwaitableResultTupleWrapper[_F, _S]:
        """Apply an asynchronous function with return type
        [trcks.ResultTuple][] to each element in the wrapped
        homogeneous [tuple][] and flatten.

        Wrapped objects short-circuit on the first [trcks.Failure][].

        Args:
            f: The asynchronous function to be applied to each element.

        Returns:
            An [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - the first [trcks.Failure][] returned by the function, or
                - a flattened awaitable [trcks.SuccessTuple][] if the
                    function returns [trcks.SuccessTuple][] for all elements.

        Example:
            >>> import asyncio
            >>> from trcks import ResultTuple
            >>> from trcks.oop import AwaitableResultTupleWrapper, TupleWrapper
            >>> async def slowly_expand_if_positive(n: int) -> ResultTuple[str, int]:
            ...     await asyncio.sleep(0.001)
            ...     if n > 0:
            ...         return "success", (n, -n)
            ...     return "failure", "negative"
            ...
            >>> awaitable_result_tuple_wrapper_1: AwaitableResultTupleWrapper[
            ...     str, int
            ... ] = (
            ...     TupleWrapper
            ...     .construct_from_tuple((1, 2))
            ...     .map_to_awaitable_result_tuple(slowly_expand_if_positive)
            ... )
            >>> awaitable_result_tuple_wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_result_tuple_wrapper_1.core_as_coroutine)
            ('success', (1, -1, 2, -2))
            >>>
            >>> awaitable_result_tuple_wrapper_2: AwaitableResultTupleWrapper[
            ...     str, int
            ... ] = (
            ...     TupleWrapper
            ...     .construct_from_tuple((1, -1, 2))
            ...     .map_to_awaitable_result_tuple(slowly_expand_if_positive)
            ... )
            >>> awaitable_result_tuple_wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_result_tuple_wrapper_2.core_as_coroutine)
            ('failure', 'negative')
        """
        return AwaitableResultTupleWrapper.construct_successes_from_tuple(
            self.core
        ).map_successes_to_awaitable_result_tuple(f)

    def map_to_awaitable_tuple(
        self, f: Callable[[_T_co], AwaitableTuple[_T]]
    ) -> AwaitableTupleWrapper[_T]:
        """Apply an asynchronous function returning a homogeneous [tuple][]
        to each element in the wrapped homogeneous [tuple][] and flatten.

        Args:
            f: The asynchronous function to be applied to each element,
                returning an awaitable homogeneous [tuple][].

        Returns:
            An [trcks.oop.AwaitableTupleWrapper][] instance with
                the flattened awaitable homogeneous [tuple][].

        Example:
            >>> import asyncio
            >>> from trcks.oop import TupleWrapper
            >>> async def slowly_duplicate(n: int) -> tuple[int, int]:
            ...     await asyncio.sleep(0.001)
            ...     return n, n
            ...
            >>> awaitable_tuple_wrapper: AwaitableTupleWrapper[int] = (
            ...     TupleWrapper
            ...     .construct_from_tuple((1, 2))
            ...     .map_to_awaitable_tuple(slowly_duplicate)
            ... )
            >>> awaitable_tuple_wrapper
            AwaitableTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_tuple_wrapper.core_as_coroutine)
            (1, 1, 2, 2)
        """
        return AwaitableTupleWrapper.construct_from_tuple(
            self.core
        ).map_to_awaitable_tuple(f)

    def map_to_result(
        self, f: Callable[[_T_co], Result[_F, _S]]
    ) -> ResultTupleWrapper[_F, _S]:
        """Apply a synchronous function with return type [trcks.Result][]
        to each element in the wrapped homogeneous [tuple][].

        Args:
            f: The synchronous function to be applied to each element.

        Returns:
            A [trcks.oop.ResultTupleWrapper][] instance with

                - the first [trcks.Failure][] returned by the function, or
                - a [trcks.SuccessTuple][] with all transformed elements if
                    the function returns [trcks.Success][] for all elements.

        Example:
            >>> from trcks import Result
            >>> from trcks.oop import TupleWrapper
            >>> def double_if_positive(n: int) -> Result[str, int]:
            ...     if n > 0:
            ...         return "success", n * 2
            ...     return "failure", "negative"
            ...
            >>> TupleWrapper.construct_from_tuple(
            ...     (1, 2, 3)
            ... ).map_to_result(double_if_positive)
            ResultTupleWrapper(core=('success', (2, 4, 6)))
            >>>
            >>> TupleWrapper.construct_from_tuple(
            ...     (1, -1, 2)
            ... ).map_to_result(double_if_positive)
            ResultTupleWrapper(core=('failure', 'negative'))
        """
        return ResultTupleWrapper.construct_successes_from_tuple(
            self.core
        ).map_successes_to_result(f)

    def map_to_result_tuple(
        self, f: Callable[[_T_co], ResultTuple[_F, _S]]
    ) -> ResultTupleWrapper[_F, _S]:
        """Apply a synchronous function with return type [trcks.ResultTuple][]
        to each element in the wrapped homogeneous [tuple][] and flatten.

        Args:
            f: The synchronous function to be applied to each element.

        Returns:
            A [trcks.oop.ResultTupleWrapper][] instance with

                - the first [trcks.Failure][] returned by the function, or
                - a flattened [trcks.SuccessTuple][] if
                    the function returns [trcks.SuccessTuple][] for all elements.

        Example:
            >>> from trcks import ResultTuple
            >>> from trcks.oop import TupleWrapper
            >>> def expand_if_positive(n: int) -> ResultTuple[str, int]:
            ...     if n > 0:
            ...         return "success", (n, -n)
            ...     return "failure", "negative"
            ...
            >>> TupleWrapper.construct_from_tuple(
            ...     (1, 2)
            ... ).map_to_result_tuple(expand_if_positive)
            ResultTupleWrapper(core=('success', (1, -1, 2, -2)))
            >>>
            >>> TupleWrapper.construct_from_tuple(
            ...     (1, -1, 2)
            ... ).map_to_result_tuple(expand_if_positive)
            ResultTupleWrapper(core=('failure', 'negative'))
        """
        return ResultTupleWrapper.construct_successes_from_tuple(
            self.core
        ).map_successes_to_result_tuple(f)

    def map_to_tuple(self, f: Callable[[_T_co], tuple[_T, ...]]) -> TupleWrapper[_T]:
        """Apply a function returning a homogeneous [tuple][] to each element
        in the wrapped homogeneous [tuple][] and flatten the result.

        Args:
            f: The function to be applied to each element,
                returning a homogeneous [tuple][].

        Returns:
            A new [trcks.oop.TupleWrapper][] instance with
                the flattened homogeneous [tuple][].

        Example:
            >>> from trcks.oop import TupleWrapper
            >>> def duplicate_integer(n: int) -> tuple[int, int]:
            ...     return n, n
            ...
            >>> tuple_wrapper: TupleWrapper[int] = (
            ...     TupleWrapper
            ...     .construct_from_tuple((1, 2, 3))
            ...     .map_to_tuple(duplicate_integer)
            ... )
            >>> tuple_wrapper
            TupleWrapper(core=(1, 1, 2, 2, 3, 3))
        """
        return TupleWrapper(t.map_to_tuple(f)(self.core))

    def tap(self, f: Callable[[_T_co], object]) -> TupleWrapper[_T_co]:
        """Apply a synchronous side effect to each element in the wrapped
        homogeneous [tuple][].

        Args:
            f: The synchronous side effect to be applied to each element.

        Returns:
            A new [trcks.oop.TupleWrapper][] instance with
                the original homogeneous [tuple][].

        Example:
            >>> from trcks.oop import TupleWrapper
            >>> def log_integer(n: int) -> None:
            ...     print(f"Received: {n}")
            ...
            >>> tuple_wrapper: TupleWrapper[int] = (
            ...     TupleWrapper
            ...     .construct_from_tuple((1, 2, 3))
            ...     .tap(log_integer)
            ... )
            Received: 1
            Received: 2
            Received: 3
            >>> tuple_wrapper
            TupleWrapper(core=(1, 2, 3))
        """
        return TupleWrapper(t.tap(f)(self.core))

    def tap_to_awaitable(
        self, f: Callable[[_T_co], Awaitable[object]]
    ) -> AwaitableTupleWrapper[_T_co]:
        """Apply an asynchronous side effect to each element in the wrapped
        homogeneous [tuple][].

        Args:
            f: The asynchronous side effect to be applied to each element.

        Returns:
            An [trcks.oop.AwaitableTupleWrapper][] instance with
                the original awaitable homogeneous [tuple][].

        Example:
            >>> import asyncio
            >>> from trcks.oop import TupleWrapper
            >>> async def slowly_log_integer(n: int) -> None:
            ...     await asyncio.sleep(0.001)
            ...     print(f"Received: {n}")
            ...
            >>> awaitable_tuple_wrapper: AwaitableTupleWrapper[int] = (
            ...     TupleWrapper
            ...     .construct_from_tuple((1, 2, 3))
            ...     .tap_to_awaitable(slowly_log_integer)
            ... )
            >>> awaitable_tuple_wrapper
            AwaitableTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_tuple_wrapper.core_as_coroutine)
            Received: 1
            Received: 2
            Received: 3
            (1, 2, 3)
        """
        return AwaitableTupleWrapper.construct_from_tuple(self.core).tap_to_awaitable(f)

    def tap_to_awaitable_result(
        self, f: Callable[[_T_co], AwaitableResult[_F, object]]
    ) -> AwaitableResultTupleWrapper[_F, _T_co]:
        """Apply an asynchronous side effect with return type [trcks.Result][]
        to each element in the wrapped homogeneous [tuple][].

        Args:
            f: The asynchronous side effect to be applied to each element.

        Returns:
            An [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - *the returned* [trcks.Failure][]
                    if the applied side effect returns a [trcks.Failure][] or
                - *the original* homogeneous [tuple][] with each element
                    repeated for the first [trcks.Success][] if all succeed.

        Example:
            >>> import asyncio
            >>> from trcks import Result, ResultTuple
            >>> from trcks.oop import AwaitableResultTupleWrapper, TupleWrapper
            >>> async def slowly_check_if_positive(n: int) -> Result[str, None]:
            ...     await asyncio.sleep(0.001)
            ...     if n > 0:
            ...         return "success", None
            ...     return "failure", "negative"
            ...
            >>> awaitable_result_tuple_wrapper_1: AwaitableResultTupleWrapper[
            ...     str, int
            ... ] = (
            ...     TupleWrapper
            ...     .construct_from_tuple((1, 2))
            ...     .tap_to_awaitable_result(slowly_check_if_positive)
            ... )
            >>> awaitable_result_tuple_wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_result_tuple_wrapper_1.core_as_coroutine)
            ('success', (1, 2))
            >>>
            >>> awaitable_result_tuple_wrapper_2: AwaitableResultTupleWrapper[
            ...     str, int
            ... ] = (
            ...     TupleWrapper
            ...     .construct_from_tuple((1, -1, 2))
            ...     .tap_to_awaitable_result(slowly_check_if_positive)
            ... )
            >>> awaitable_result_tuple_wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_result_tuple_wrapper_2.core_as_coroutine)
            ('failure', 'negative')
        """
        return AwaitableResultTupleWrapper.construct_successes_from_tuple(
            self.core
        ).tap_successes_to_awaitable_result(f)

    def tap_to_awaitable_result_tuple(
        self, f: Callable[[_T_co], AwaitableResultTuple[_F, object]]
    ) -> AwaitableResultTupleWrapper[_F, _T_co]:
        """Apply an asynchronous side effect with return type
        [trcks.ResultTuple][] to each element in the wrapped
        homogeneous [tuple][].

        Args:
            f: The asynchronous side effect to be applied to each element.

        Returns:
            An [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - *the returned* [trcks.Failure][]
                    if the applied side effect returns a [trcks.Failure][] or
                - *the original* element repeated once per element in the side
                    effect output for each element if all succeed.

        Example:
            >>> import asyncio
            >>> from trcks import ResultTuple
            >>> from trcks.oop import AwaitableResultTupleWrapper, TupleWrapper
            >>> async def audit(n: int) -> ResultTuple[str, None]:
            ...     await asyncio.sleep(0.001)
            ...     if n > 0:
            ...         return "success", (None, None)
            ...     return "failure", "negative"
            ...
            >>> awaitable_result_tuple_wrapper_1: AwaitableResultTupleWrapper[
            ...     str, int
            ... ] = (
            ...     TupleWrapper
            ...     .construct_from_tuple((1, 2))
            ...     .tap_to_awaitable_result_tuple(audit)
            ... )
            >>> awaitable_result_tuple_wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_result_tuple_wrapper_1.core_as_coroutine)
            ('success', (1, 1, 2, 2))
            >>>
            >>> awaitable_result_tuple_wrapper_2: AwaitableResultTupleWrapper[
            ...     str, int
            ... ] = (
            ...     TupleWrapper
            ...     .construct_from_tuple((1, -1, 2))
            ...     .tap_to_awaitable_result_tuple(audit)
            ... )
            >>> awaitable_result_tuple_wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_result_tuple_wrapper_2.core_as_coroutine)
            ('failure', 'negative')
        """
        return AwaitableResultTupleWrapper.construct_successes_from_tuple(
            self.core
        ).tap_successes_to_awaitable_result_tuple(f)

    def tap_to_awaitable_tuple(
        self, f: Callable[[_T_co], AwaitableTuple[object]]
    ) -> AwaitableTupleWrapper[_T_co]:
        """Apply an asynchronous side effect returning a [tuple][]
        to each element in the wrapped homogeneous [tuple][].

        Args:
            f: The asynchronous side effect to be applied to each element,
                returning an awaitable homogeneous [tuple][].

        Returns:
            An [trcks.oop.AwaitableTupleWrapper][] instance with
                the original awaitable homogeneous [tuple][].

        Example:
            >>> import asyncio
            >>> from trcks.oop import AwaitableTupleWrapper, TupleWrapper
            >>> async def write_to_disk(n: int) -> tuple[str, str]:
            ...     await asyncio.sleep(0.001)
            ...     print(f"Wrote {n} to disk.")
            ...     return str(n), str(n)
            ...
            >>> awaitable_tuple_wrapper: AwaitableTupleWrapper[int] = (
            ...     TupleWrapper
            ...     .construct_from_tuple((1, 2, 3))
            ...     .tap_to_awaitable_tuple(write_to_disk)
            ... )
            >>> awaitable_tuple_wrapper
            AwaitableTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_tuple_wrapper.core_as_coroutine)
            Wrote 1 to disk.
            Wrote 2 to disk.
            Wrote 3 to disk.
            (1, 1, 2, 2, 3, 3)
        """
        return AwaitableTupleWrapper.construct_from_tuple(
            self.core
        ).tap_to_awaitable_tuple(f)

    def tap_to_result(
        self, f: Callable[[_T_co], Result[_F, object]]
    ) -> ResultTupleWrapper[_F, _T_co]:
        """Apply a synchronous side effect with return type [trcks.Result][]
        to each element in the wrapped homogeneous [tuple][].

        Args:
            f: The synchronous side effect to be applied to each element.

        Returns:
            A [trcks.oop.ResultTupleWrapper][] instance with

                - *the returned* [trcks.Failure][]
                    if the applied side effect returns a [trcks.Failure][] or
                - *the original* [trcks.SuccessTuple][]
                    if the applied side effect returns [trcks.Success][]
                    for all elements.

        Example:
            >>> from trcks import Result
            >>> from trcks.oop import TupleWrapper
            >>> def audit(n: int) -> Result[str, None]:
            ...     if n > 0:
            ...         return "success", None
            ...     return "failure", "negative"
            ...
            >>> TupleWrapper.construct_from_tuple(
            ...     (1, 2)
            ... ).tap_to_result(audit)
            ResultTupleWrapper(core=('success', (1, 2)))
            >>>
            >>> TupleWrapper.construct_from_tuple(
            ...     (1, -1, 2)
            ... ).tap_to_result(audit)
            ResultTupleWrapper(core=('failure', 'negative'))
        """
        return ResultTupleWrapper.construct_successes_from_tuple(
            self.core
        ).tap_successes_to_result(f)

    def tap_to_result_tuple(
        self, f: Callable[[_T_co], ResultTuple[_F, object]]
    ) -> ResultTupleWrapper[_F, _T_co]:
        """Apply a synchronous side effect with return type [trcks.ResultTuple][]
        to each element in the wrapped homogeneous [tuple][].

        Args:
            f: The synchronous side effect to be applied to each element.

        Returns:
            A [trcks.oop.ResultTupleWrapper][] instance with

                - *the returned* [trcks.Failure][]
                    if the applied side effect returns a [trcks.Failure][] or
                - *the original* [trcks.SuccessTuple][] element repeated once
                    per element in the side effect output if the applied side effect
                    returns [trcks.SuccessTuple][] for all elements.

        Example:
            >>> from trcks import ResultTuple
            >>> from trcks.oop import TupleWrapper
            >>> def audit(n: int) -> ResultTuple[str, None]:
            ...     if n > 0:
            ...         return "success", (None, None)
            ...     return "failure", "negative"
            ...
            >>> TupleWrapper.construct_from_tuple(
            ...     (7,)
            ... ).tap_to_result_tuple(audit)
            ResultTupleWrapper(core=('success', (7, 7)))
            >>>
            >>> TupleWrapper.construct_from_tuple(
            ...     (1, -1)
            ... ).tap_to_result_tuple(audit)
            ResultTupleWrapper(core=('failure', 'negative'))
        """
        return ResultTupleWrapper.construct_successes_from_tuple(
            self.core
        ).tap_successes_to_result_tuple(f)

    def tap_to_tuple(
        self, f: Callable[[_T_co], tuple[object, ...]]
    ) -> TupleWrapper[_T_co]:
        """Apply a side effect returning a [tuple][] to each element
        in the wrapped homogeneous [tuple][].

        Args:
            f: The side effect to be applied to each element.

        Returns:
            A new [trcks.oop.TupleWrapper][] instance with
                the original homogeneous [tuple][].

        Example:
            >>> from trcks.oop import TupleWrapper
            >>> def get_divisors(n: int) -> tuple[int, ...]:
            ...     candidates = range(1, n + 1)
            ...     return tuple(c for c in candidates if n % c == 0)
            ...
            >>> tuple_wrapper: TupleWrapper[int] = (
            ...     TupleWrapper
            ...     .construct_from_tuple((1, 2, 3, 4))
            ...     .tap_to_tuple(get_divisors)
            ... )
            >>> tuple_wrapper
            TupleWrapper(core=(1, 2, 2, 3, 3, 4, 4, 4))
        """
        return TupleWrapper(t.tap_to_tuple(f)(self.core))


class Wrapper(_Wrapper[_T_co]):
    """Type-safe and immutable wrapper for arbitrary objects.

    The wrapped object can be accessed via the attribute `trcks.oop.Wrapper.core`.
    The `trcks.oop.Wrapper.map*` methods allow method chaining.
    The `trcks.oop.Wrapper.tap*` methods allow for side effects
    without changing the wrapped object.

    Example:
        The string `"Hello"` is wrapped and manipulated in the following example.
        Finally, the result is unwrapped:

        >>> wrapper = (
        ...     Wrapper(core="Hello")
        ...     .map(len)
        ...     .tap(lambda n: print(f"Received {n}."))
        ...     .map(lambda n: f"Length: {n}")
        ... )
        Received 5.
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
            A new [trcks.oop.Wrapper][] instance with the wrapped object.

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
            A new [trcks.oop.Wrapper][] instance
                with the result of the function application.

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
            A [trcks.oop.AwaitableWrapper][] instance with
                the result of the function application.

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
        """Apply an asynchronous function with return type [trcks.Result][]
        to the wrapped object.

        Args:
            f: The asynchronous function to be applied.

        Returns:
            A [trcks.oop.AwaitableResultWrapper][] instance with
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
            ...         return "failure", "negative value"
            ...     return "success", x
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

    def map_to_awaitable_result_tuple(
        self, f: Callable[[_T_co], AwaitableResultTuple[_F, _S]]
    ) -> AwaitableResultTupleWrapper[_F, _S]:
        """Apply an asynchronous function with return type
        [trcks.ResultTuple][] to the wrapped object.

        Args:
            f: The asynchronous function to be applied.

        Returns:
            A [trcks.oop.AwaitableResultTupleWrapper][] instance with
                the result of the function application.

        Example:
            >>> import asyncio
            >>> from trcks import AwaitableResultTuple
            >>> from trcks.oop import Wrapper
            >>> async def validate(x: float) -> AwaitableResultTuple[str, float]:
            ...     await asyncio.sleep(0.001)
            ...     if x < 0:
            ...         return "failure", "negative value"
            ...     return "success", (x, x * 2)
            ...
            >>> wrapper = (
            ...     Wrapper
            ...     .construct(5.0)
            ...     .map_to_awaitable_result_tuple(validate)
            ... )
            >>> wrapper
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper.core_as_coroutine)
            ('success', (5.0, 10.0))
        """
        return AwaitableResultTupleWrapper(f(self.core))

    def map_to_awaitable_tuple(
        self, f: Callable[[_T_co], AwaitableTuple[_T]]
    ) -> AwaitableTupleWrapper[_T]:
        """Apply an asynchronous function returning a homogeneous [tuple][]
        to the wrapped object.

        Args:
            f: The asynchronous function to be applied, returning a
                homogeneous [tuple][].

        Returns:
            A [trcks.oop.AwaitableTupleWrapper][] instance with
                the result of the function application.

        Example:
            >>> import asyncio
            >>> from trcks.oop import Wrapper
            >>> async def slowly_duplicate(n: int) -> tuple[int, int]:
            ...     await asyncio.sleep(0.001)
            ...     return n, n
            ...
            >>> async def main() -> tuple[int, ...]:
            ...     awaitable_tuple_wrapper = (
            ...         Wrapper.construct(7).map_to_awaitable_tuple(slowly_duplicate)
            ...     )
            ...     result_tuple = await awaitable_tuple_wrapper.core
            ...     assert len(result_tuple) == 2
            ...     return result_tuple
            ...
            >>> asyncio.run(main())
            (7, 7)
        """
        return AwaitableTupleWrapper(f(self.core))

    def map_to_result(
        self, f: Callable[[_T_co], Result[_F, _S]]
    ) -> ResultWrapper[_F, _S]:
        """Apply a synchronous function with return type [trcks.Result][]
        to the wrapped object.

        Args:
            f: The synchronous function to be applied.

        Returns:
            A [trcks.oop.ResultWrapper][] instance with
                the result of the function application.

        Example:
            >>> Wrapper.construct(-1).map_to_result(
            ...     lambda n: ("success", n)
            ...     if n >= 0
            ...     else ("failure", "negative value")
            ... )
            ResultWrapper(core=('failure', 'negative value'))
        """
        return ResultWrapper(f(self.core))

    def map_to_result_tuple(
        self, f: Callable[[_T_co], ResultTuple[_F, _S]]
    ) -> ResultTupleWrapper[_F, _S]:
        """Apply a synchronous function with return type [trcks.ResultTuple][]
        to the wrapped object.

        Args:
            f: The synchronous function to be applied.

        Returns:
            A [trcks.oop.ResultTupleWrapper][] instance with
                the result of the function application.

        Example:
            >>> from trcks import ResultTuple
            >>> Wrapper.construct(-1).map_to_result_tuple(
            ...     lambda n: ("success", (n, n))
            ...     if n >= 0
            ...     else ("failure", "negative value")
            ... )
            ResultTupleWrapper(core=('failure', 'negative value'))
        """
        return ResultTupleWrapper(f(self.core))

    def map_to_tuple(self, f: Callable[[_T_co], tuple[_T, ...]]) -> TupleWrapper[_T]:
        """Apply a function returning a homogeneous [tuple][]
        to the wrapped object.

        Args:
            f: The function to be applied, returning a [tuple][].

        Returns:
            A [trcks.oop.TupleWrapper][] instance with
                the result of the function application.

        Example:
            >>> from trcks.oop import Wrapper
            >>> def duplicate(n: int) -> tuple[int, int]:
            ...     return n, n
            ...
            >>> Wrapper.construct(3).map_to_tuple(duplicate)
            TupleWrapper(core=(3, 3))
        """
        return TupleWrapper(f(self.core))

    def tap(self, f: Callable[[_T_co], object]) -> Wrapper[_T_co]:
        """Apply a synchronous side effect to the wrapped object.

        Args:
            f: The synchronous side effect to be applied.

        Returns:
            A new [trcks.oop.Wrapper][] instance with the original wrapped object,
                allowing for further method chaining.

        Example:
            >>> wrapper = Wrapper.construct(5).tap(lambda n: print(f"Number: {n}"))
            Number: 5
            >>> wrapper
            Wrapper(core=5)
        """
        return self.map(i.tap(f))

    def tap_to_awaitable(
        self, f: Callable[[_T_co], Awaitable[object]]
    ) -> AwaitableWrapper[_T_co]:
        """Apply an asynchronous side effect to the wrapped object.

        Args:
            f: The asynchronous side effect to be applied.

        Returns:
            A [trcks.oop.AwaitableWrapper][] instance with the original wrapped object.

        Example:
            >>> import asyncio
            >>> from trcks.oop import Wrapper
            >>> async def write_to_disk(s: str) -> None:
            ...     await asyncio.sleep(0.001)
            ...     print(f"Wrote '{s}' to disk.")
            ...
            >>> awaitable_wrapper = Wrapper.construct(
            ...     "Hello, world!"
            ... ).tap_to_awaitable(write_to_disk)
            >>> awaitable_wrapper
            AwaitableWrapper(core=<coroutine object ...>)
            >>> value = asyncio.run(awaitable_wrapper.core_as_coroutine)
            Wrote 'Hello, world!' to disk.
            >>> value
            'Hello, world!'
        """
        return AwaitableWrapper.construct(self.core).tap_to_awaitable(f)

    def tap_to_awaitable_result(
        self, f: Callable[[_T_co], AwaitableResult[_F, object]]
    ) -> AwaitableResultWrapper[_F, _T_co]:
        """Apply an asynchronous side effect with return type [trcks.Result][]
        to the wrapped object.

        Args:
            f: The asynchronous side effect to be applied.

        Returns:
            A [trcks.oop.AwaitableResultWrapper][] instance with

                - *the returned* [trcks.Failure][]
                    if the given side effect returns a [trcks.Failure][] or
                - a [trcks.Success][] instance containing *the original* wrapped object
                    if the given side effect returns a [trcks.Success][].

        Example:
            >>> import asyncio
            >>> from trcks import Result
            >>> from trcks.oop import Wrapper
            >>> async def write_to_disk(s: str, path: str) -> Result[str, None]:
            ...     if path != "output.txt":
            ...         return "failure", "write error"
            ...     await asyncio.sleep(0.001)
            ...     print(f"Wrote '{s}' to file {path}.")
            ...     return "success", None
            ...
            >>> awaitable_result_wrapper_1 = Wrapper.construct(
            ...     "Hello, world!"
            ... ).tap_to_awaitable_result(
            ...     lambda s: write_to_disk(s, "destination.txt")
            ... )
            >>> awaitable_result_wrapper_1
            AwaitableResultWrapper(core=<coroutine object ...>)
            >>> result_1 = asyncio.run(awaitable_result_wrapper_1.core_as_coroutine)
            >>> result_1
            ('failure', 'write error')
            >>> awaitable_result_wrapper_2 = Wrapper.construct(
            ...     "Hello, world!"
            ... ).tap_to_awaitable_result(
            ...     lambda s: write_to_disk(s, "output.txt")
            ... )
            >>> awaitable_result_wrapper_2
            AwaitableResultWrapper(core=<coroutine object ...>)
            >>> result_2 = asyncio.run(awaitable_result_wrapper_2.core_as_coroutine)
            Wrote 'Hello, world!' to file output.txt.
            >>> result_2
            ('success', 'Hello, world!')
        """
        return AwaitableResultWrapper.construct_success(
            self.core
        ).tap_success_to_awaitable_result(f)

    def tap_to_awaitable_result_tuple(
        self, f: Callable[[_T_co], AwaitableResultTuple[_F, object]]
    ) -> AwaitableResultTupleWrapper[_F, _T_co]:
        """Apply an asynchronous side effect with return type
        [trcks.ResultTuple][] to the wrapped object.

        Args:
            f: The asynchronous side effect to be applied.

        Returns:
            A [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - *the returned* [trcks.Failure][]
                    if the given side effect returns a [trcks.Failure][] or
                - *the original* wrapped object repeated once per element
                    in the side effect output if the given side effect
                    returns [trcks.SuccessTuple][].

        Example:
            >>> import asyncio
            >>> from trcks import AwaitableResultTuple
            >>> from trcks.oop import Wrapper
            >>> async def write_twice(
            ...     s: str,
            ... ) -> AwaitableResultTuple[str, None]:
            ...     await asyncio.sleep(0.001)
            ...     print(f"Wrote '{s}' twice.")
            ...     return "success", (None, None)
            ...
            >>> wrapper = Wrapper.construct(
            ...     "Hello, world!"
            ... ).tap_to_awaitable_result_tuple(write_twice)
            >>> wrapper
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> result = asyncio.run(wrapper.core_as_coroutine)
            Wrote 'Hello, world!' twice.
            >>> result
            ('success', ('Hello, world!', 'Hello, world!'))
        """
        return AwaitableResultTupleWrapper.construct_successes(
            self.core
        ).tap_successes_to_awaitable_result_tuple(f)

    def tap_to_awaitable_tuple(
        self, f: Callable[[_T_co], AwaitableTuple[object]]
    ) -> AwaitableTupleWrapper[_T_co]:
        """Apply an asynchronous side effect returning a [tuple][]
        to the wrapped object.

        Args:
            f: The asynchronous side effect to be applied,
                returning a [tuple][].

        Returns:
            A [trcks.oop.AwaitableTupleWrapper][] instance with
                the original wrapped object repeated once per item returned by the
                side effect.

        Example:
            >>> import asyncio
            >>> from trcks.oop import Wrapper
            >>> async def write_to_disk(n: int) -> tuple[str, str]:
            ...     await asyncio.sleep(0.001)
            ...     print(f"Wrote {n} to disk.")
            ...     return "left", "right"
            ...
            >>> awaitable_tuple_wrapper = Wrapper.construct(
            ...     3
            ... ).tap_to_awaitable_tuple(write_to_disk)
            >>> asyncio.run(awaitable_tuple_wrapper.core_as_coroutine)
            Wrote 3 to disk.
            (3, 3)
        """
        return AwaitableTupleWrapper.construct(self.core).tap_to_awaitable_tuple(f)

    def tap_to_result(
        self, f: Callable[[_T_co], Result[_F, object]]
    ) -> ResultWrapper[_F, _T_co]:
        """Apply a synchronous side effect with return type [trcks.Result][]
        to the wrapped object.

        Args:
            f: The synchronous side effect to be applied.

        Returns:
            A [trcks.oop.ResultWrapper][] instance with

                - *the returned* [trcks.Failure][]
                    if the given side effect returns a [trcks.Failure][] or
                - a [trcks.Success][] instance containing *the original* wrapped object
                    if the given side effect returns a [trcks.Success][].

        Example:
            >>> from trcks import Result
            >>> from trcks.oop import Wrapper
            >>> def print_positive_float(x: float) -> Result[str, None]:
            ...     if x <= 0:
            ...         return "failure", "not positive"
            ...     return "success", print(f"Positive float: {x}")
            ...
            >>> result_wrapper_1 = Wrapper.construct(-2.3).tap_to_result(
            ...     print_positive_float
            ... )
            >>> result_wrapper_1
            ResultWrapper(core=('failure', 'not positive'))
            >>> result_wrapper_2 = Wrapper.construct(3.5).tap_to_result(
            ...     print_positive_float
            ... )
            Positive float: 3.5
            >>> result_wrapper_2
            ResultWrapper(core=('success', 3.5))
        """
        return ResultWrapper.construct_success(self.core).tap_success_to_result(f)

    def tap_to_result_tuple(
        self, f: Callable[[_T_co], ResultTuple[_F, object]]
    ) -> ResultTupleWrapper[_F, _T_co]:
        """Apply a synchronous side effect with return type [trcks.ResultTuple][]
        to the wrapped object.

        Args:
            f: The synchronous side effect to be applied.

        Returns:
            A [trcks.oop.ResultTupleWrapper][] instance with

                - *the returned* [trcks.Failure][]
                    if the given side effect returns a [trcks.Failure][] or
                - *the original* [trcks.SuccessTuple][] element repeated once
                    per element in the side effect output if the given side effect
                    returns [trcks.SuccessTuple][].

        Example:
            >>> from trcks import ResultTuple
            >>> from trcks.oop import Wrapper
            >>> def print_positive_float(x: float) -> ResultTuple[str, None]:
            ...     if x <= 0:
            ...         return "failure", "not positive"
            ...     return (
            ...         "success",
            ...         (print(f"Positive float: {x}"), print(f"Positive float: {x}"))
            ...     )
            >>> result_tuple_wrapper_1 = Wrapper.construct(
            ...     -2.3
            ... ).tap_to_result_tuple(print_positive_float)
            >>> result_tuple_wrapper_1
            ResultTupleWrapper(core=('failure', 'not positive'))
            >>> result_tuple_wrapper_2 = Wrapper.construct(
            ...     3.5
            ... ).tap_to_result_tuple(print_positive_float)
            Positive float: 3.5
            Positive float: 3.5
            >>> result_tuple_wrapper_2
            ResultTupleWrapper(core=('success', (3.5, 3.5)))
        """
        return ResultTupleWrapper.construct_successes(
            self.core
        ).tap_successes_to_result_tuple(f)

    def tap_to_tuple(
        self, f: Callable[[_T_co], tuple[object, ...]]
    ) -> TupleWrapper[_T_co]:
        """Apply a side effect returning a [tuple][] to the
        wrapped object.

        Args:
            f: The side effect to be applied, returning a
                [tuple][].

        Returns:
            A [trcks.oop.TupleWrapper][] instance with the original wrapped
                object repeated once per item returned by the side effect.

        Example:
            >>> from trcks.oop import Wrapper
            >>> def write_to_disk(n: int) -> tuple[str, str]:
            ...     print(f"Wrote {n} to disk.")
            ...     return "left", "right"
            ...
            >>> Wrapper.construct(3).tap_to_tuple(write_to_disk)
            Wrote 3 to disk.
            TupleWrapper(core=(3, 3))
        """
        return TupleWrapper.construct(self.core).tap_to_tuple(f)
