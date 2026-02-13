"""Object-oriented interface for [trcks][].

This module provides wrapper classes for processing values of the following types
in a method-chaining style:

- [collections.abc.Awaitable][]
- [collections.abc.Sequence][]
- [trcks.AwaitableResult][]
- [trcks.AwaitableSequence][]
- [trcks.Result][]
- [trcks.ResultSequence][]

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

    Variable and type assignments for intermediate values might help  to clarify
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

from collections.abc import Awaitable, Callable, Sequence
from typing import Generic, Literal

from trcks import AwaitableResult, AwaitableSequence, Result, ResultSequence
from trcks._typing import Never, TypeVar, override
from trcks.fp.monads import awaitable as a
from trcks.fp.monads import awaitable_result as ar
from trcks.fp.monads import awaitable_sequence as as_
from trcks.fp.monads import identity as i
from trcks.fp.monads import result as r
from trcks.fp.monads import result_sequence as rs
from trcks.fp.monads import sequence as s

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

    _core: _T_co

    def __init__(self, core: _T_co) -> None:
        """Construct wrapper.

        Args:
            core: The value to be wrapped.
        """
        super().__init__()
        self._core = core

    @override
    def __repr__(self) -> str:
        """Return a string representation of the wrapper."""
        return f"{self.__class__.__name__}(core={self._core!r})"

    @property
    def core(self) -> _T_co:
        """The wrapped object."""
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


class AwaitableResultWrapper(_AwaitableWrapper[Result[_F_default_co, _S_default_co]]):
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

    @property
    async def track(self) -> Literal["failure", "success"]:
        """First element of the awaited attribute
        `trcks.oop.AwaitableResultWrapper.core`.

        Example:
            >>> import asyncio
            >>> from trcks.oop import AwaitableResultWrapper
            >>> track_coroutine = AwaitableResultWrapper.construct_failure(42).track
            >>> track_coroutine
            <coroutine object ...>
            >>> asyncio.run(track_coroutine)
            'failure'
        """
        return (await self.core)[0]

    @property
    async def value(self) -> _F_default_co | _S_default_co:
        """Second element of the awaited attribute
        `trcks.oop.AwaitableResultWrapper.core`.

        Example:
            >>> import asyncio
            >>> from trcks.oop import AwaitableResultWrapper
            >>> value_coroutine = AwaitableResultWrapper.construct_failure(42).value
            >>> value_coroutine
            <coroutine object ...>
            >>> asyncio.run(value_coroutine)
            42
        """
        return (await self.core)[1]


class AwaitableSequenceWrapper(_AwaitableWrapper[Sequence[_T_co]]):
    """Type-safe and immutable wrapper for [trcks.AwaitableSequence][] objects.

    The wrapped object can be accessed
    via the attribute `trcks.oop.AwaitableSequenceWrapper.core`.
    The `trcks.oop.AwaitableSequenceWrapper.map*` methods allow method chaining.
    The `trcks.oop.AwaitableSequenceWrapper.tap*` methods allow for side effects
    without changing the wrapped sequence.

    Example:
        >>> import asyncio
        >>> from collections.abc import Sequence
        >>> from trcks.oop import AwaitableSequenceWrapper
        >>> async def double(x: int) -> int:
        ...     await asyncio.sleep(0.001)
        ...     return x * 2
        ...
        >>> async def main() -> Sequence[int]:
        ...     awaitable_sequence_wrapper = (
        ...         AwaitableSequenceWrapper
        ...         .construct_from_sequence((1, 2, 3))
        ...         .map_to_awaitable(double)
        ...     )
        ...     return await awaitable_sequence_wrapper.core_as_coroutine
        ...
        >>> asyncio.run(main())
        [2, 4, 6]
    """

    @staticmethod
    def construct(value: _T) -> AwaitableSequenceWrapper[_T]:
        """Construct and wrap a [trcks.AwaitableSequence][] object from a value.

        Args:
            value: The value to be wrapped.

        Returns:
            A new [trcks.oop.AwaitableSequenceWrapper][] instance with
                the wrapped [trcks.AwaitableSequence][] object.

        Example:
            >>> import asyncio
            >>> from trcks.oop import AwaitableSequenceWrapper
            >>> awaitable_sequence_wrapper = AwaitableSequenceWrapper.construct(42)
            >>> awaitable_sequence_wrapper
            AwaitableSequenceWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_sequence_wrapper.core_as_coroutine)
            [42]
        """
        return AwaitableSequenceWrapper(as_.construct(value))

    @staticmethod
    def construct_from_awaitable(
        awtbl: Awaitable[_T],
    ) -> AwaitableSequenceWrapper[_T]:
        """Construct and wrap a [trcks.AwaitableSequence][] from an awaitable value.

        Args:
            awtbl: The awaitable value to be wrapped.

        Returns:
            A new [trcks.oop.AwaitableSequenceWrapper][] instance with
                the wrapped [trcks.AwaitableSequence][] object.

        Example:
            >>> import asyncio
            >>> from trcks.oop import AwaitableSequenceWrapper
            >>> async def get_value() -> int:
            ...     await asyncio.sleep(0.001)
            ...     return 7
            ...
            >>> awaitable_sequence_wrapper = (
            ...     AwaitableSequenceWrapper
            ...     .construct_from_awaitable(get_value())
            ... )
            >>> awaitable_sequence_wrapper
            AwaitableSequenceWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_sequence_wrapper.core_as_coroutine)
            [7]
        """
        return AwaitableSequenceWrapper(as_.construct_from_awaitable(awtbl))

    @staticmethod
    def construct_from_sequence(
        seq: Sequence[_T],
    ) -> AwaitableSequenceWrapper[_T]:
        """Construct and wrap a [trcks.AwaitableSequence][] from a sequence.

        Args:
            seq: The sequence to be wrapped.

        Returns:
            A new [trcks.oop.AwaitableSequenceWrapper][] instance with
                the wrapped [trcks.AwaitableSequence][] object.

        Example:
            >>> import asyncio
            >>> from trcks.oop import AwaitableSequenceWrapper
            >>> awaitable_sequence_wrapper = (
            ...     AwaitableSequenceWrapper
            ...     .construct_from_sequence((1, 2, 3))
            ... )
            >>> awaitable_sequence_wrapper
            AwaitableSequenceWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_sequence_wrapper.core_as_coroutine)
            (1, 2, 3)
        """
        return AwaitableSequenceWrapper(as_.construct_from_sequence(seq))

    def map(self, f: Callable[[_T_co], _T]) -> AwaitableSequenceWrapper[_T]:
        """Apply a synchronous function to each element in the wrapped
        [trcks.AwaitableSequence][] object.

        Args:
            f: The synchronous function to be applied to each element.

        Returns:
            A new [trcks.oop.AwaitableSequenceWrapper][] instance with
                the wrapped [trcks.AwaitableSequence][] object containing
                the results of applying the function to each element.

        Example:
            >>> import asyncio
            >>> from collections.abc import Sequence
            >>> from trcks.oop import AwaitableSequenceWrapper
            >>> async def main() -> Sequence[int]:
            ...     return await (
            ...         AwaitableSequenceWrapper
            ...         .construct_from_sequence((1, 2, 3))
            ...         .map(lambda x: x * 2)
            ...         .core_as_coroutine
            ...     )
            ...
            >>> asyncio.run(main())
            [2, 4, 6]
        """
        return AwaitableSequenceWrapper(as_.map_(f)(self.core))

    def map_to_awaitable(
        self, f: Callable[[_T_co], Awaitable[_T]]
    ) -> AwaitableSequenceWrapper[_T]:
        """Apply an asynchronous function to each element in the wrapped
        [trcks.AwaitableSequence][] object.

        Args:
            f: The asynchronous function to be applied to each element.

        Returns:
            A new [trcks.oop.AwaitableSequenceWrapper][] instance with
                the wrapped [trcks.AwaitableSequence][] object containing
                the results of applying the function to each element.

        Example:
            >>> import asyncio
            >>> from collections.abc import Sequence
            >>> from trcks.oop import AwaitableSequenceWrapper
            >>> async def add_one(x: int) -> int:
            ...     await asyncio.sleep(0.001)
            ...     return x + 1
            ...
            >>> async def main() -> Sequence[int]:
            ...     return await (
            ...         AwaitableSequenceWrapper
            ...         .construct_from_sequence((1, 2, 3))
            ...         .map_to_awaitable(add_one)
            ...         .core_as_coroutine
            ...     )
            ...
            >>> asyncio.run(main())
            [2, 3, 4]
        """
        return AwaitableSequenceWrapper(as_.map_to_awaitable(f)(self.core))

    def map_to_awaitable_sequence(
        self, f: Callable[[_T_co], AwaitableSequence[_T]]
    ) -> AwaitableSequenceWrapper[_T]:
        """Apply an asynchronous function returning a [collections.abc.Sequence][]
        to each element in the wrapped [trcks.AwaitableSequence][] and flatten.

        Args:
            f: The asynchronous function to be applied to each element,
                returning a [trcks.AwaitableSequence][].

        Returns:
            A new [trcks.oop.AwaitableSequenceWrapper][] instance with
                the flattened [trcks.AwaitableSequence][] object.

        Example:
            >>> import asyncio
            >>> from collections.abc import Sequence
            >>> from trcks.oop import AwaitableSequenceWrapper
            >>> async def duplicate(x: int) -> list[int]:
            ...     await asyncio.sleep(0.001)
            ...     return [x, x]
            ...
            >>> async def main() -> Sequence[int]:
            ...     return await (
            ...         AwaitableSequenceWrapper
            ...         .construct_from_sequence((1, 2))
            ...         .map_to_awaitable_sequence(duplicate)
            ...         .core_as_coroutine
            ...     )
            ...
            >>> asyncio.run(main())
            [1, 1, 2, 2]
        """
        return AwaitableSequenceWrapper(as_.map_to_awaitable_sequence(f)(self.core))

    def map_to_sequence(
        self, f: Callable[[_T_co], Sequence[_T]]
    ) -> AwaitableSequenceWrapper[_T]:
        """Apply a synchronous function returning a sequence to each element in
        the wrapped [trcks.AwaitableSequence][] object and flatten.

        Args:
            f: The synchronous function to be applied to each element,
                returning a sequence.

        Returns:
            A new [trcks.oop.AwaitableSequenceWrapper][] instance with
                the flattened [trcks.AwaitableSequence][] object.

        Example:
            >>> import asyncio
            >>> from collections.abc import Sequence
            >>> from trcks.oop import AwaitableSequenceWrapper
            >>> async def main() -> Sequence[int]:
            ...     return await (
            ...         AwaitableSequenceWrapper
            ...         .construct_from_sequence((1, 2, 3))
            ...         .map_to_sequence(lambda x: (x, -x))
            ...         .core_as_coroutine
            ...     )
            ...
            >>> asyncio.run(main())
            [1, -1, 2, -2, 3, -3]
        """
        return AwaitableSequenceWrapper(as_.map_to_sequence(f)(self.core))

    def tap(self, f: Callable[[_T_co], object]) -> AwaitableSequenceWrapper[_T_co]:
        """Apply a synchronous side effect to each element in the wrapped
        [trcks.AwaitableSequence][] object.

        Args:
            f: The synchronous side effect to be applied to each element.

        Returns:
            A new [trcks.oop.AwaitableSequenceWrapper][] instance with
                the original [trcks.AwaitableSequence][] object.

        Example:
            >>> import asyncio
            >>> from collections.abc import Sequence
            >>> from trcks.oop import AwaitableSequenceWrapper
            >>> async def main() -> Sequence[int]:
            ...     return await (
            ...         AwaitableSequenceWrapper
            ...         .construct_from_sequence((1, 2, 3))
            ...         .tap(lambda x: print(f"Processing: {x}"))
            ...         .core_as_coroutine
            ...     )
            ...
            >>> asyncio.run(main())
            Processing: 1
            Processing: 2
            Processing: 3
            [1, 2, 3]
        """
        return AwaitableSequenceWrapper(as_.tap(f)(self.core))

    def tap_to_awaitable(
        self, f: Callable[[_T_co], Awaitable[object]]
    ) -> AwaitableSequenceWrapper[_T_co]:
        """Apply an asynchronous side effect to each element in the wrapped
        [trcks.AwaitableSequence][] object.

        Args:
            f: The asynchronous side effect to be applied to each element.

        Returns:
            A new [trcks.oop.AwaitableSequenceWrapper][] instance with
                the original [trcks.AwaitableSequence][] object.

        Example:
            >>> import asyncio
            >>> from collections.abc import Sequence
            >>> from trcks.oop import AwaitableSequenceWrapper
            >>> async def log_async(x: int) -> None:
            ...     await asyncio.sleep(0.001)
            ...     print(f"Logged: {x}")
            ...
            >>> async def main() -> Sequence[int]:
            ...     return await (
            ...         AwaitableSequenceWrapper
            ...         .construct_from_sequence((1, 2))
            ...         .tap_to_awaitable(log_async)
            ...         .core_as_coroutine
            ...     )
            ...
            >>> asyncio.run(main())
            Logged: 1
            Logged: 2
            [1, 2]
        """
        return AwaitableSequenceWrapper(as_.tap_to_awaitable(f)(self.core))

    def tap_to_awaitable_sequence(
        self, f: Callable[[_T_co], AwaitableSequence[object]]
    ) -> AwaitableSequenceWrapper[_T_co]:
        """Apply an asynchronous side effect returning a [trcks.AwaitableSequence][]
        to each element in the wrapped [trcks.AwaitableSequence][] object.

        Args:
            f: The asynchronous side effect to be applied to each element,
                returning a [trcks.AwaitableSequence][].

        Returns:
            A new [trcks.oop.AwaitableSequenceWrapper][] instance with
                the original [trcks.AwaitableSequence][] object.

        Example:
            >>> import asyncio
            >>> from collections.abc import Sequence
            >>> from trcks.oop import AwaitableSequenceWrapper
            >>> async def echo_twice(x: int) -> list[str]:
            ...     await asyncio.sleep(0.001)
            ...     return [str(x), str(x)]
            ...
            >>> async def main() -> Sequence[int]:
            ...     return await (
            ...         AwaitableSequenceWrapper
            ...         .construct_from_sequence((1, 2))
            ...         .tap_to_awaitable_sequence(echo_twice)
            ...         .core_as_coroutine
            ...     )
            ...
            >>> asyncio.run(main())
            [1, 1, 2, 2]
        """
        return AwaitableSequenceWrapper(as_.tap_to_awaitable_sequence(f)(self.core))

    def tap_to_sequence(
        self, f: Callable[[_T_co], Sequence[object]]
    ) -> AwaitableSequenceWrapper[_T_co]:
        """Apply a synchronous side effect returning a sequence to each element in
        the wrapped [trcks.AwaitableSequence][] object.

        Args:
            f: The synchronous side effect to be applied to each element,
                returning a sequence.

        Returns:
            A new [trcks.oop.AwaitableSequenceWrapper][] instance with
                the original [trcks.AwaitableSequence][] object.

        Example:
            >>> import asyncio
            >>> from collections.abc import Sequence
            >>> from trcks.oop import AwaitableSequenceWrapper
            >>> async def main() -> Sequence[int]:
            ...     return await (
            ...         AwaitableSequenceWrapper
            ...         .construct_from_sequence((1, 2))
            ...         .tap_to_sequence(lambda x: (x, x))
            ...         .core_as_coroutine
            ...     )
            ...
            >>> asyncio.run(main())
            [1, 1, 2, 2]
        """
        return AwaitableSequenceWrapper(as_.tap_to_sequence(f)(self.core))


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

    def map_to_awaitable_sequence(
        self, f: Callable[[_T_co], AwaitableSequence[_T]]
    ) -> AwaitableSequenceWrapper[_T]:
        """Apply an asynchronous function returning a [collections.abc.Sequence][]
        to the wrapped [collections.abc.Awaitable][] object.

        Args:
            f: The asynchronous function to be applied, returning an awaitable
                [collections.abc.Sequence][].

        Returns:
            A new [trcks.oop.AwaitableSequenceWrapper][] instance with
                the result of the function application.

        Example:
            >>> import asyncio
            >>> from collections.abc import Sequence
            >>> from trcks.oop import AwaitableWrapper
            >>> async def duplicate_async(x: int) -> Sequence[int]:
            ...     await asyncio.sleep(0.001)
            ...     return [x, x]
            ...
            >>> awaitable_sequence_wrapper = (
            ...     AwaitableWrapper
            ...     .construct(21)
            ...     .map_to_awaitable_sequence(duplicate_async)
            ... )
            >>> awaitable_sequence_wrapper
            AwaitableSequenceWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_sequence_wrapper.core_as_coroutine)
            [21, 21]
        """
        return AwaitableSequenceWrapper(a.map_to_awaitable(f)(self.core))

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
            ...         lambda x: (
            ...             ("success", x) if x >= 0 else ("failure", "negative value")
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

    def map_to_sequence(
        self, f: Callable[[_T_co], Sequence[_T]]
    ) -> AwaitableSequenceWrapper[_T]:
        """Apply a synchronous function returning a [collections.abc.Sequence][]
        to the wrapped [collections.abc.Awaitable][] object.

        Args:
            f: The synchronous function to be applied.

        Returns:
            A new [trcks.oop.AwaitableSequenceWrapper][] instance with
                the result of the function application.

        Example:
            >>> import asyncio
            >>> from collections.abc import Sequence
            >>> from trcks.oop import AwaitableWrapper
            >>> awaitable_sequence_wrapper = (
            ...     AwaitableWrapper
            ...     .construct(3)
            ...     .map_to_sequence(lambda x: [x, -x])
            ... )
            >>> awaitable_sequence_wrapper
            AwaitableSequenceWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_sequence_wrapper.core_as_coroutine)
            [3, -3]
        """
        return AwaitableSequenceWrapper(a.map_(f)(self.core))

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

    def tap_to_awaitable_sequence(
        self, f: Callable[[_T_co], AwaitableSequence[object]]
    ) -> AwaitableSequenceWrapper[_T_co]:
        """Apply an asynchronous side effect returning a [collections.abc.Sequence][]
        to the wrapped [collections.abc.Awaitable][] object.

        Args:
            f: The asynchronous side effect to be applied,
                returning an awaitable [collections.abc.Sequence][].

        Returns:
            A new [trcks.oop.AwaitableSequenceWrapper][] instance with
                the original awaitable wrapped object repeated
                according to the number of items returned by the side effect.

        Example:
            >>> import asyncio
            >>> from collections.abc import Sequence
            >>> from trcks.oop import AwaitableWrapper
            >>> async def duplicate_with_log_async(x: int) -> Sequence[int]:
            ...     await asyncio.sleep(0.001)
            ...     print(f"Processing: {x}")
            ...     return [x, x]
            ...
            >>> async def main() -> Sequence[int]:
            ...     return await (
            ...         AwaitableWrapper
            ...         .construct(21)
            ...         .tap_to_awaitable_sequence(duplicate_with_log_async)
            ...         .core_as_coroutine
            ...     )
            ...
            >>> asyncio.run(main())
            Processing: 21
            [21, 21]
        """
        return AwaitableSequenceWrapper.construct_from_awaitable(
            self.core
        ).tap_to_awaitable_sequence(f)

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

    def tap_to_sequence(
        self, f: Callable[[_T_co], Sequence[object]]
    ) -> AwaitableSequenceWrapper[_T_co]:
        """Apply a synchronous side effect returning a [collections.abc.Sequence][]
        to the wrapped [collections.abc.Awaitable][] object.

        Args:
            f: The synchronous side effect to be applied,
                returning a [collections.abc.Sequence][].

        Returns:
            A new [trcks.oop.AwaitableSequenceWrapper][] instance with
                the original awaitable wrapped object repeated
                according to the number of items returned by the side effect.

        Example:
            >>> import asyncio
            >>> from collections.abc import Sequence
            >>> from trcks.oop import AwaitableWrapper
            >>> def duplicate_with_log(x: int) -> Sequence[object]:
            ...     print(f"Processing: {x}")
            ...     return [x, x]
            ...
            >>> async def main() -> Sequence[int]:
            ...     return await (
            ...         AwaitableWrapper
            ...         .construct(42)
            ...         .tap_to_sequence(duplicate_with_log)
            ...         .core_as_coroutine
            ...     )
            ...
            >>> asyncio.run(main())
            Processing: 42
            [42, 42]
        """
        return AwaitableSequenceWrapper.construct_from_awaitable(
            self.core
        ).tap_to_sequence(f)


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

    def map_failure_to_result_sequence(
        self, f: Callable[[_F_default_co], ResultSequence[_F, _S]]
    ) -> ResultSequenceWrapper[_F, _S_default_co | _S]:
        """Apply a synchronous function with return type [trcks.ResultSequence][]
        to the wrapped [trcks.Failure][] object.

        Wrapped [trcks.Success][] objects are passed on unchanged.

        Args:
            f: The synchronous function to be applied.

        Returns:
            A [trcks.oop.ResultSequenceWrapper][] instance with

                - the result of the function application if
                    the original [trcks.Result][] is a failure, or
                - the original [trcks.Result][] object (wrapped as a sequence)
                    if it is a success.

        Example:
            >>> from trcks import ResultSequence
            >>> from trcks.oop import ResultWrapper
            >>> def expand_error(s: str) -> ResultSequence[str, float]:
            ...     if s == "not found":
            ...         return "success", [0.0, 1.0]
            ...     return "failure", s
            ...
            >>> ResultWrapper.construct_failure(
            ...     "not found"
            ... ).map_failure_to_result_sequence(expand_error)
            ResultSequenceWrapper(core=('success', [0.0, 1.0]))
            >>>
            >>> ResultWrapper.construct_failure(
            ...     "other error"
            ... ).map_failure_to_result_sequence(expand_error)
            ResultSequenceWrapper(core=('failure', 'other error'))
            >>>
            >>> ResultWrapper.construct_success(
            ...     42
            ... ).map_failure_to_result_sequence(expand_error)
            ResultSequenceWrapper(core=('success', [42]))
        """
        return ResultSequenceWrapper.construct_from_result(
            self.core
        ).map_failure_to_result_sequence(f)

    def map_failure_to_sequence(
        self, f: Callable[[_F_default_co], Sequence[_S]]
    ) -> ResultSequenceWrapper[Never, _S_default_co | _S]:
        """Apply a synchronous function returning a [collections.abc.Sequence][]
        to the wrapped [trcks.Failure][] object.

        The failure is converted to a [trcks.SuccessSequence][].
        Wrapped [trcks.Success][] objects are passed on unchanged.

        Args:
            f: The synchronous function to be applied,
                returning a [collections.abc.Sequence][].

        Returns:
            A [trcks.oop.ResultSequenceWrapper][] instance with

                - a [trcks.SuccessSequence][] containing the result
                    of the function application if
                    the original [trcks.Result][] is a failure, or
                - the original [trcks.Result][] object (wrapped as a sequence)
                    if it is a success.

        Example:
            >>> from trcks.oop import ResultWrapper
            >>> def recover(s: str) -> list[float]:
            ...     if s == "not found":
            ...         return [0.0, 1.0]
            ...     return []
            ...
            >>> ResultWrapper.construct_failure(
            ...     "not found"
            ... ).map_failure_to_sequence(recover)
            ResultSequenceWrapper(core=('success', [0.0, 1.0]))
            >>>
            >>> ResultWrapper.construct_failure(
            ...     "other error"
            ... ).map_failure_to_sequence(recover)
            ResultSequenceWrapper(core=('success', []))
            >>>
            >>> ResultWrapper.construct_success(
            ...     42
            ... ).map_failure_to_sequence(recover)
            ResultSequenceWrapper(core=('success', [42]))
        """
        return ResultSequenceWrapper.construct_from_result(
            self.core
        ).map_failure_to_sequence(f)

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

    def map_success_to_result_sequence(
        self, f: Callable[[_S_default_co], ResultSequence[_F, _S]]
    ) -> ResultSequenceWrapper[_F_default_co | _F, _S]:
        """Apply a synchronous function with return type [trcks.ResultSequence][]
        to the wrapped [trcks.Success][] object.

        Wrapped [trcks.Failure][] objects are passed on unchanged.

        Args:
            f: The synchronous function to be applied.

        Returns:
            A [trcks.oop.ResultSequenceWrapper][] instance with

                - the original [trcks.Result][] object if it is a failure, or
                - the result of the function application if
                    the original [trcks.Result][] is a success.

        Example:
            >>> from trcks import ResultSequence
            >>> from trcks.oop import ResultWrapper
            >>> def expand(x: float) -> ResultSequence[str, float]:
            ...     if x < 0:
            ...         return "failure", "negative"
            ...     return "success", [x, x * 2]
            ...
            >>> ResultWrapper.construct_failure(
            ...     "not found"
            ... ).map_success_to_result_sequence(expand)
            ResultSequenceWrapper(core=('failure', 'not found'))
            >>>
            >>> ResultWrapper.construct_success(
            ...     5.0
            ... ).map_success_to_result_sequence(expand)
            ResultSequenceWrapper(core=('success', [5.0, 10.0]))
            >>>
            >>> ResultWrapper.construct_success(
            ...     -5.0
            ... ).map_success_to_result_sequence(expand)
            ResultSequenceWrapper(core=('failure', 'negative'))
        """
        return ResultSequenceWrapper.construct_from_result(
            self.core
        ).map_successes_to_result_sequence(f)

    def map_success_to_sequence(
        self, f: Callable[[_S_default_co], Sequence[_S]]
    ) -> ResultSequenceWrapper[_F_default_co, _S]:
        """Apply a synchronous function returning a [collections.abc.Sequence][]
        to the wrapped [trcks.Success][] object.

        Wrapped [trcks.Failure][] objects are passed on unchanged.

        Args:
            f: The synchronous function to be applied,
                returning a [collections.abc.Sequence][].

        Returns:
            A [trcks.oop.ResultSequenceWrapper][] instance with

                - the original [trcks.Result][] object if it is a failure, or
                - a [trcks.SuccessSequence][] containing the result
                    of the function application if
                    the original [trcks.Result][] is a success.

        Example:
            >>> from trcks.oop import ResultWrapper
            >>> def duplicate(x: float) -> list[float]:
            ...     return [x, x]
            ...
            >>> ResultWrapper.construct_failure(
            ...     "not found"
            ... ).map_success_to_sequence(duplicate)
            ResultSequenceWrapper(core=('failure', 'not found'))
            >>>
            >>> ResultWrapper.construct_success(
            ...     5.0
            ... ).map_success_to_sequence(duplicate)
            ResultSequenceWrapper(core=('success', [5.0, 5.0]))
        """
        return ResultSequenceWrapper.construct_from_result(
            self.core
        ).map_successes_to_sequence(f)

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

    def tap_failure_to_result_sequence(
        self, f: Callable[[_F_default_co], ResultSequence[object, _S]]
    ) -> ResultSequenceWrapper[_F_default_co, _S_default_co | _S]:
        """Apply a synchronous side effect with return type [trcks.ResultSequence][]
        to the wrapped [trcks.Failure][] object.

        Wrapped [trcks.Success][] objects are passed on without side effects.

        Args:
            f: The synchronous side effect to be applied.

        Returns:
            A [trcks.oop.ResultSequenceWrapper][] instance with

                - *the original* [trcks.Failure][]
                    if the applied side effect returns a [trcks.Failure][],
                - *the returned* [trcks.SuccessSequence][]
                    if the applied side effect returns a [trcks.SuccessSequence][] and
                - *the original* [trcks.Success][] (wrapped as a sequence)
                    if no side effect was applied.

        Example:
            >>> from trcks import ResultSequence
            >>> from trcks.oop import ResultWrapper
            >>> def attempt_recover(s: str) -> ResultSequence[None, int]:
            ...     if s == "retry":
            ...         return "success", [99]
            ...     return "failure", None
            ...
            >>> ResultWrapper.construct_failure(
            ...     "retry"
            ... ).tap_failure_to_result_sequence(attempt_recover)
            ResultSequenceWrapper(core=('success', [99]))
            >>>
            >>> ResultWrapper.construct_failure(
            ...     "fatal"
            ... ).tap_failure_to_result_sequence(attempt_recover)
            ResultSequenceWrapper(core=('failure', 'fatal'))
            >>>
            >>> ResultWrapper.construct_success(
            ...     42
            ... ).tap_failure_to_result_sequence(attempt_recover)
            ResultSequenceWrapper(core=('success', [42]))
        """
        return ResultSequenceWrapper.construct_from_result(
            self.core
        ).tap_failure_to_result_sequence(f)

    def tap_failure_to_sequence(
        self, f: Callable[[_F_default_co], Sequence[object]]
    ) -> ResultSequenceWrapper[Never, _F_default_co | _S_default_co]:
        """Apply a synchronous side effect returning a [collections.abc.Sequence][]
        to the wrapped [trcks.Failure][] object.

        The failure is converted to a [trcks.SuccessSequence][] where
        the original failure value is repeated once per element in
        the sequence returned by the side effect.

        Wrapped [trcks.Success][] objects are passed on without side effects.

        Args:
            f: The synchronous side effect to be applied,
                returning a [collections.abc.Sequence][].

        Returns:
            A [trcks.oop.ResultSequenceWrapper][] instance with

                - a [trcks.SuccessSequence][] containing the original failure
                    repeated once per element
                    in the sequence returned by the side effect
                    if the original [trcks.Result][] is a failure, or
                - *the original* [trcks.Success][] (wrapped as a sequence)
                    if no side effect was applied.

        Example:
            >>> from trcks.oop import ResultWrapper
            >>> def log_err(e: str) -> list[None]:
            ...     print(f"Error logged: {e}")
            ...     print(f"Alert sent: {e}")
            ...     return [None, None]
            ...
            >>> ResultWrapper.construct_failure(
            ...     "critical"
            ... ).tap_failure_to_sequence(log_err)
            Error logged: critical
            Alert sent: critical
            ResultSequenceWrapper(core=('success', ['critical', 'critical']))
            >>>
            >>> ResultWrapper.construct_success(
            ...     42
            ... ).tap_failure_to_sequence(log_err)
            ResultSequenceWrapper(core=('success', [42]))
        """
        return ResultSequenceWrapper.construct_from_result(
            self.core
        ).tap_failure_to_sequence(f)

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

    def tap_success_to_result_sequence(
        self, f: Callable[[_S_default_co], ResultSequence[_F, object]]
    ) -> ResultSequenceWrapper[_F_default_co | _F, _S_default_co]:
        """Apply a synchronous side effect with return type [trcks.ResultSequence][]
        to the wrapped [trcks.Success][] object.

        Wrapped [trcks.Failure][] objects are passed on without side effects.

        Args:
            f: The synchronous side effect to be applied.

        Returns:
            A [trcks.oop.ResultSequenceWrapper][] instance with

                - *the original* [trcks.Failure][] if no side effect was applied,
                - *the returned* [trcks.Failure][]
                    if the applied side effect returns a [trcks.Failure][] and
                - *the original* [trcks.Success][] (wrapped and repeated once
                    per element in the side effect output) if the applied side effect
                    returns [trcks.SuccessSequence][].

        Example:
            >>> from trcks import ResultSequence
            >>> from trcks.oop import ResultWrapper
            >>> def audit(x: int) -> ResultSequence[str, None]:
            ...     if x > 0:
            ...         return "success", [None, None]
            ...     return "failure", "bad"
            ...
            >>> ResultWrapper.construct_failure(
            ...     "oops"
            ... ).tap_success_to_result_sequence(audit)
            ResultSequenceWrapper(core=('failure', 'oops'))
            >>>
            >>> ResultWrapper.construct_success(
            ...     7
            ... ).tap_success_to_result_sequence(audit)
            ResultSequenceWrapper(core=('success', [7, 7]))
            >>>
            >>> ResultWrapper.construct_success(
            ...     -1
            ... ).tap_success_to_result_sequence(audit)
            ResultSequenceWrapper(core=('failure', 'bad'))
        """
        return ResultSequenceWrapper.construct_from_result(
            self.core
        ).tap_successes_to_result_sequence(f)

    def tap_success_to_sequence(
        self, f: Callable[[_S_default_co], Sequence[object]]
    ) -> ResultSequenceWrapper[_F_default_co, _S_default_co]:
        """Apply a synchronous side effect returning a [collections.abc.Sequence][]
        to the wrapped [trcks.Success][] object.

        The original success value is repeated once per element
        in the sequence returned by the side effect.

        Wrapped [trcks.Failure][] objects are passed on without side effects.

        Args:
            f: The synchronous side effect to be applied,
                returning a [collections.abc.Sequence][].

        Returns:
            A [trcks.oop.ResultSequenceWrapper][] instance with

                - *the original* [trcks.Failure][] if no side effect was applied, or
                - a [trcks.SuccessSequence][] where the original element is repeated
                    once per element in the sequence returned by the side effect.

        Example:
            >>> from trcks.oop import ResultWrapper
            >>> def log_mult(x: int) -> list[None]:
            ...     print(f"v={x}")
            ...     print(f"v={x}")
            ...     return [None, None]
            ...
            >>> ResultWrapper.construct_failure(
            ...     "error"
            ... ).tap_success_to_sequence(log_mult)
            ResultSequenceWrapper(core=('failure', 'error'))
            >>>
            >>> ResultWrapper.construct_success(
            ...     7
            ... ).tap_success_to_sequence(log_mult)
            v=7
            v=7
            ResultSequenceWrapper(core=('success', [7, 7]))
        """
        return ResultSequenceWrapper.construct_from_result(
            self.core
        ).tap_successes_to_sequence(f)


class ResultSequenceWrapper(_ResultWrapper[_F_default_co, Sequence[_S_default_co]]):
    """Type-safe and immutable wrapper for [trcks.ResultSequence][] objects.

    The wrapped object can be accessed via the attribute
    `trcks.oop.ResultSequenceWrapper.core`.
    The `trcks.oop.ResultSequenceWrapper.map*` methods allow method chaining.
    The `trcks.oop.ResultSequenceWrapper.tap*` methods allow for side effects.

    Example:
        >>> from trcks.oop import ResultSequenceWrapper
        >>> result_sequence_wrapper = (
        ...     ResultSequenceWrapper
        ...     .construct_successes_from_sequence([1, 2, 3])
        ...     .map_successes(lambda x: x * 2)
        ...     .tap_successes(lambda x: print(f"Processed: {x}"))
        ... )
        Processed: 2
        Processed: 4
        Processed: 6
        >>> result_sequence_wrapper
        ResultSequenceWrapper(core=('success', [2, 4, 6]))
        >>> result_sequence_wrapper.core
        ('success', [2, 4, 6])
    """

    @staticmethod
    def construct_failure(value: _F) -> ResultSequenceWrapper[_F, Never]:
        """Construct and wrap a [trcks.Failure][] object from a value.

        Args:
            value: The value to be wrapped.

        Returns:
            A new [trcks.oop.ResultSequenceWrapper][] instance with
                the wrapped [trcks.Failure][] object.

        Example:
            >>> ResultSequenceWrapper.construct_failure("not found")
            ResultSequenceWrapper(core=('failure', 'not found'))
        """
        return ResultSequenceWrapper(rs.construct_failure(value))

    @staticmethod
    def construct_from_result(
        rslt: Result[_F_default, _S_default],
    ) -> ResultSequenceWrapper[_F_default, _S_default]:
        """Construct and wrap a [trcks.ResultSequence][] object from a
        [trcks.Result][] object.

        Args:
            rslt: The [trcks.Result][] object to be wrapped.

        Returns:
            A new [trcks.oop.ResultSequenceWrapper][] instance with
                the wrapped [trcks.ResultSequence][] object.

        Example:
            >>> from trcks.oop import ResultSequenceWrapper
            >>> ResultSequenceWrapper.construct_from_result(("success", 7))
            ResultSequenceWrapper(core=('success', [7]))
            >>> ResultSequenceWrapper.construct_from_result(("failure", "oops"))
            ResultSequenceWrapper(core=('failure', 'oops'))
        """
        return ResultSequenceWrapper(rs.construct_from_result(rslt))

    @staticmethod
    def construct_successes(value: _S) -> ResultSequenceWrapper[Never, _S]:
        """Construct and wrap a [trcks.SuccessSequence][] object from a value.

        Args:
            value: The value to be wrapped.

        Returns:
            A new [trcks.oop.ResultSequenceWrapper][] instance with
                the wrapped [trcks.SuccessSequence][] object.

        Example:
            >>> ResultSequenceWrapper.construct_successes(42)
            ResultSequenceWrapper(core=('success', [42]))
        """
        return ResultSequenceWrapper(rs.construct_successes(value))

    @staticmethod
    def construct_successes_from_sequence(
        seq: Sequence[_S],
    ) -> ResultSequenceWrapper[Never, _S]:
        """Construct and wrap a [trcks.SuccessSequence][] object from a sequence.

        Args:
            seq: The sequence to be wrapped.

        Returns:
            A new [trcks.oop.ResultSequenceWrapper][] instance with
                the wrapped [trcks.SuccessSequence][] object.

        Example:
            >>> ResultSequenceWrapper.construct_successes_from_sequence([1, 2, 3])
            ResultSequenceWrapper(core=('success', [1, 2, 3]))
        """
        return ResultSequenceWrapper(rs.construct_successes_from_sequence(seq))

    def map_failure(
        self, f: Callable[[_F_default_co], _F]
    ) -> ResultSequenceWrapper[_F, _S_default_co]:
        """Apply a synchronous function to the wrapped [trcks.Failure][] object.

        Wrapped [trcks.SuccessSequence][] objects are passed on unchanged.

        Args:
            f: The synchronous function to be applied.

        Returns:
            A new [trcks.oop.ResultSequenceWrapper][] instance with

                - the result of the function application if
                    the original [trcks.ResultSequence][] is a failure, or
                - the original [trcks.ResultSequence][] object if it is a success.

        Example:
            >>> ResultSequenceWrapper.construct_failure("not found").map_failure(
            ...     lambda e: f"err: {e}"
            ... )
            ResultSequenceWrapper(core=('failure', 'err: not found'))
            >>>
            >>> ResultSequenceWrapper.construct_successes_from_sequence(
            ...     [1, 2]
            ... ).map_failure(lambda e: f"err: {e}")
            ResultSequenceWrapper(core=('success', [1, 2]))
        """
        return ResultSequenceWrapper(rs.map_failure(f)(self.core))

    def map_failure_to_result(
        self, f: Callable[[_F_default_co], Result[_F, _S]]
    ) -> ResultSequenceWrapper[_F, _S_default_co | _S]:
        """Apply a synchronous function with return type [trcks.Result][]
        to the wrapped [trcks.Failure][] object.

        Wrapped [trcks.SuccessSequence][] objects are passed on unchanged.

        Args:
            f: The synchronous function to be applied.

        Returns:
            A new [trcks.oop.ResultSequenceWrapper][] instance with

                - the result of the function application if
                    the original [trcks.ResultSequence][] is a failure, or
                - the original [trcks.ResultSequence][] object if it is a success.

        Example:
            >>> from trcks import Result
            >>> from trcks.oop import ResultSequenceWrapper
            >>> def recover(e: str) -> Result[str, int]:
            ...     if e == "not found":
            ...         return "success", 0
            ...     return "failure", e
            ...
            >>> ResultSequenceWrapper.construct_failure(
            ...     "not found"
            ... ).map_failure_to_result(recover)
            ResultSequenceWrapper(core=('success', [0]))
            >>>
            >>> ResultSequenceWrapper.construct_successes_from_sequence(
            ...     [1, 2]
            ... ).map_failure_to_result(recover)
            ResultSequenceWrapper(core=('success', [1, 2]))
        """
        mapped_f: Callable[
            [ResultSequence[_F_default_co, _S_default_co]],
            ResultSequence[_F, _S_default_co | _S],
        ] = rs.map_failure_to_result(f)
        return ResultSequenceWrapper(mapped_f(self.core))

    def map_failure_to_result_sequence(
        self, f: Callable[[_F_default_co], ResultSequence[_F, _S]]
    ) -> ResultSequenceWrapper[_F, _S_default_co | _S]:
        """Apply a synchronous function with return type [trcks.ResultSequence][]
        to the wrapped [trcks.Failure][] object.

        Wrapped [trcks.SuccessSequence][] objects are passed on unchanged.

        Args:
            f: The synchronous function to be applied.

        Returns:
            A new [trcks.oop.ResultSequenceWrapper][] instance with

                - the result of the function application if
                    the original [trcks.ResultSequence][] is a failure, or
                - the original [trcks.ResultSequence][] object if it is a success.

        Example:
            >>> from trcks import ResultSequence
            >>> from trcks.oop import ResultSequenceWrapper
            >>> def recover(e: str) -> ResultSequence[str, int]:
            ...     if e == "not found":
            ...         return "success", [0]
            ...     return "failure", e
            ...
            >>> ResultSequenceWrapper.construct_failure(
            ...     "not found"
            ... ).map_failure_to_result_sequence(recover)
            ResultSequenceWrapper(core=('success', [0]))
            >>>
            >>> ResultSequenceWrapper.construct_successes_from_sequence(
            ...     [1, 2]
            ... ).map_failure_to_result_sequence(recover)
            ResultSequenceWrapper(core=('success', [1, 2]))
        """
        mapped_f: Callable[
            [ResultSequence[_F_default_co, _S_default_co]],
            ResultSequence[_F, _S_default_co | _S],
        ] = rs.map_failure_to_result_sequence(f)
        return ResultSequenceWrapper(mapped_f(self.core))

    def map_failure_to_sequence(
        self, f: Callable[[_F_default_co], Sequence[_S]]
    ) -> ResultSequenceWrapper[Never, _S_default_co | _S]:
        """Apply a synchronous function returning a sequence
        to the wrapped [trcks.Failure][] object.

        Wrapped [trcks.SuccessSequence][] objects are passed on unchanged.

        Args:
            f: The synchronous function to be applied.

        Returns:
            A new [trcks.oop.ResultSequenceWrapper][] instance with

                - a [trcks.SuccessSequence][] containing the result of
                    the function application if
                    the original [trcks.ResultSequence][] is a failure, or
                - the original [trcks.ResultSequence][] object if it is a success.

        Example:
            >>> from trcks.oop import ResultSequenceWrapper
            >>> def recover(e: str) -> list[int]:
            ...     if e == "not found":
            ...         return [0]
            ...     return []
            ...
            >>> ResultSequenceWrapper.construct_failure(
            ...     "not found"
            ... ).map_failure_to_sequence(recover)
            ResultSequenceWrapper(core=('success', [0]))
            >>>
            >>> ResultSequenceWrapper.construct_successes_from_sequence(
            ...     [1, 2]
            ... ).map_failure_to_sequence(recover)
            ResultSequenceWrapper(core=('success', [1, 2]))
        """
        mapped_f: Callable[
            [ResultSequence[_F_default_co, _S_default_co]],
            ResultSequence[Never, _S_default_co | _S],
        ] = rs.map_failure_to_sequence(f)
        return ResultSequenceWrapper(mapped_f(self.core))

    def map_successes(
        self, f: Callable[[_S_default_co], _S]
    ) -> ResultSequenceWrapper[_F_default_co, _S]:
        """Apply a synchronous function to each element in the wrapped
        [trcks.SuccessSequence][].

        Wrapped [trcks.Failure][] objects are passed on unchanged.

        Args:
            f: The synchronous function to be applied to each success element.

        Returns:
            A new [trcks.oop.ResultSequenceWrapper][] instance with

                - the original [trcks.ResultSequence][] object if it is a failure, or
                - a [trcks.SuccessSequence][] with transformed elements if
                    the original [trcks.ResultSequence][] is a success.

        Example:
            >>> ResultSequenceWrapper.construct_failure("not found").map_successes(
            ...     lambda x: x * 2
            ... )
            ResultSequenceWrapper(core=('failure', 'not found'))
            >>>
            >>> ResultSequenceWrapper.construct_successes_from_sequence(
            ...     [1, 2, 3]
            ... ).map_successes(lambda x: x * 2)
            ResultSequenceWrapper(core=('success', [2, 4, 6]))
        """
        return ResultSequenceWrapper(rs.map_successes(f)(self.core))

    def map_successes_to_result(
        self, f: Callable[[_S_default_co], Result[_F, _S]]
    ) -> ResultSequenceWrapper[_F_default_co | _F, _S]:
        """Apply a synchronous function with return type [trcks.Result][]
        to each element in the wrapped [trcks.SuccessSequence][].

        Wrapped [trcks.Failure][] objects are passed on unchanged.

        Args:
            f: The synchronous function to be applied to each success element.

        Returns:
            A new [trcks.oop.ResultSequenceWrapper][] instance with

                - the original [trcks.ResultSequence][] object if it is a failure, or
                - the first [trcks.Failure][] returned by the function, or
                - a [trcks.SuccessSequence][] with all transformed elements if
                    the function returns [trcks.Success][] for all elements.

        Example:
            >>> from trcks import Result
            >>> from trcks.oop import ResultSequenceWrapper
            >>> def check(x: int) -> Result[str, int]:
            ...     if x > 0:
            ...         return "success", x * 2
            ...     return "failure", "bad"
            ...
            >>> ResultSequenceWrapper.construct_successes_from_sequence(
            ...     [1, 2]
            ... ).map_successes_to_result(check)
            ResultSequenceWrapper(core=('success', [2, 4]))
            >>>
            >>> ResultSequenceWrapper.construct_successes_from_sequence(
            ...     [1, -1, 2]
            ... ).map_successes_to_result(check)
            ResultSequenceWrapper(core=('failure', 'bad'))
        """
        mapped_f: Callable[
            [ResultSequence[_F_default_co, _S_default_co]],
            ResultSequence[_F_default_co | _F, _S],
        ] = rs.map_successes_to_result(f)
        return ResultSequenceWrapper(mapped_f(self.core))

    def map_successes_to_result_sequence(
        self, f: Callable[[_S_default_co], ResultSequence[_F, _S]]
    ) -> ResultSequenceWrapper[_F_default_co | _F, _S]:
        """Apply a synchronous function with return type [trcks.ResultSequence][]
        to each element in the wrapped [trcks.SuccessSequence][] and flatten.

        Wrapped [trcks.Failure][] objects are passed on unchanged.

        Args:
            f: The synchronous function to be applied to each success element.

        Returns:
            A new [trcks.oop.ResultSequenceWrapper][] instance with

                - the original [trcks.ResultSequence][] object if it is a failure, or
                - the first [trcks.Failure][] returned by the function, or
                - a flattened [trcks.SuccessSequence][] if the function returns
                    [trcks.SuccessSequence][] for all elements.

        Example:
            >>> from trcks import ResultSequence
            >>> from trcks.oop import ResultSequenceWrapper
            >>> def expand(x: int) -> ResultSequence[str, int]:
            ...     if x > 0:
            ...         return "success", [x, -x]
            ...     return "failure", "bad"
            ...
            >>> ResultSequenceWrapper.construct_successes_from_sequence(
            ...     [1, 2]
            ... ).map_successes_to_result_sequence(expand)
            ResultSequenceWrapper(core=('success', [1, -1, 2, -2]))
            >>>
            >>> ResultSequenceWrapper.construct_successes_from_sequence(
            ...     [1, -1, 2]
            ... ).map_successes_to_result_sequence(expand)
            ResultSequenceWrapper(core=('failure', 'bad'))
        """
        mapped_f: Callable[
            [ResultSequence[_F_default_co, _S_default_co]],
            ResultSequence[_F_default_co | _F, _S],
        ] = rs.map_successes_to_result_sequence(f)
        return ResultSequenceWrapper(mapped_f(self.core))

    def map_successes_to_sequence(
        self, f: Callable[[_S_default_co], Sequence[_S]]
    ) -> ResultSequenceWrapper[_F_default_co, _S]:
        """Apply a synchronous function returning a sequence
        to each element in the wrapped [trcks.SuccessSequence][] and flatten.

        Wrapped [trcks.Failure][] objects are passed on unchanged.

        Args:
            f: The synchronous function to be applied to each success element.

        Returns:
            A new [trcks.oop.ResultSequenceWrapper][] instance with

                - the original [trcks.ResultSequence][] object if it is a failure, or
                - a flattened [trcks.SuccessSequence][] if
                    the original [trcks.ResultSequence][] is a success.

        Example:
            >>> from trcks.oop import ResultSequenceWrapper
            >>> ResultSequenceWrapper.construct_successes_from_sequence(
            ...     [1, 2]
            ... ).map_successes_to_sequence(lambda x: [x, -x])
            ResultSequenceWrapper(core=('success', [1, -1, 2, -2]))
        """
        return ResultSequenceWrapper(rs.map_successes_to_sequence(f)(self.core))

    def tap_failure(
        self, f: Callable[[_F_default_co], object]
    ) -> ResultSequenceWrapper[_F_default_co, _S_default_co]:
        """Apply a synchronous side effect to the wrapped [trcks.Failure][] object.

        Wrapped [trcks.SuccessSequence][] objects are passed on without side effects.

        Args:
            f: The synchronous side effect to be applied.

        Returns:
            A new [trcks.oop.ResultSequenceWrapper][] instance
                with the original [trcks.ResultSequence][] object,
                allowing for further method chaining.

        Example:
            >>> result_sequence_wrapper_1 = ResultSequenceWrapper.construct_failure(
            ...     "oops"
            ... ).tap_failure(lambda e: print(f"Error: {e}"))
            Error: oops
            >>> result_sequence_wrapper_1
            ResultSequenceWrapper(core=('failure', 'oops'))
            >>> result_sequence_wrapper_2 = (
            ...     ResultSequenceWrapper.construct_successes(1).tap_failure(
            ...         lambda e: print(f"Error: {e}")
            ...     )
            ... )
            >>> result_sequence_wrapper_2
            ResultSequenceWrapper(core=('success', [1]))
        """
        return ResultSequenceWrapper(rs.tap_failure(f)(self.core))

    def tap_failure_to_result(
        self, f: Callable[[_F_default_co], Result[object, _S]]
    ) -> ResultSequenceWrapper[_F_default_co, _S_default_co | _S]:
        """Apply a synchronous side effect with return type [trcks.Result][]
        to the wrapped [trcks.Failure][] object.

        Wrapped [trcks.SuccessSequence][] objects are passed on without side effects.

        Args:
            f: The synchronous side effect to be applied.

        Returns:
            A new [trcks.oop.ResultSequenceWrapper][] instance with

                - *the original* [trcks.Failure][]
                    if the applied side effect returns a [trcks.Failure][],
                - *the returned* [trcks.Success][] (wrapped as a sequence)
                    if the applied side effect returns a [trcks.Success][] and
                - *the original* [trcks.SuccessSequence][]
                    if no side effect was applied.

        Example:
            >>> from trcks import Result
            >>> from trcks.oop import ResultSequenceWrapper
            >>> def retry_lookup(e: str) -> Result[None, int]:
            ...     if e == "not found":
            ...         print("Retrying...")
            ...         return "success", 42
            ...     return "failure", None
            ...
            >>> ResultSequenceWrapper.construct_failure(
            ...     "not found"
            ... ).tap_failure_to_result(retry_lookup)
            Retrying...
            ResultSequenceWrapper(core=('success', [42]))
            >>>
            >>> ResultSequenceWrapper.construct_failure(
            ...     "fatal"
            ... ).tap_failure_to_result(retry_lookup)
            ResultSequenceWrapper(core=('failure', 'fatal'))
        """
        tapped_f: Callable[
            [ResultSequence[_F_default_co, _S_default_co]],
            ResultSequence[_F_default_co, _S_default_co | _S],
        ] = rs.tap_failure_to_result(f)
        return ResultSequenceWrapper(tapped_f(self.core))

    def tap_failure_to_result_sequence(
        self, f: Callable[[_F_default_co], ResultSequence[object, _S]]
    ) -> ResultSequenceWrapper[_F_default_co, _S_default_co | _S]:
        """Apply a synchronous side effect with return type [trcks.ResultSequence][]
        to the wrapped [trcks.Failure][] object.

        Wrapped [trcks.SuccessSequence][] objects are passed on without side effects.

        Args:
            f: The synchronous side effect to be applied.

        Returns:
            A new [trcks.oop.ResultSequenceWrapper][] instance with

                - *the original* [trcks.Failure][]
                    if the applied side effect returns a [trcks.Failure][],
                - *the returned* [trcks.SuccessSequence][]
                    if the applied side effect returns a [trcks.SuccessSequence][] and
                - *the original* [trcks.SuccessSequence][]
                    if no side effect was applied.

        Example:
            >>> from trcks import ResultSequence
            >>> from trcks.oop import ResultSequenceWrapper
            >>> def attempt_recover(e: str) -> ResultSequence[None, int]:
            ...     if e == "retry":
            ...         return "success", [99]
            ...     return "failure", None
            ...
            >>> ResultSequenceWrapper.construct_failure(
            ...     "retry"
            ... ).tap_failure_to_result_sequence(attempt_recover)
            ResultSequenceWrapper(core=('success', [99]))
            >>>
            >>> ResultSequenceWrapper.construct_failure(
            ...     "fatal"
            ... ).tap_failure_to_result_sequence(attempt_recover)
            ResultSequenceWrapper(core=('failure', 'fatal'))
        """
        tapped_f: Callable[
            [ResultSequence[_F_default_co, _S_default_co]],
            ResultSequence[_F_default_co, _S_default_co | _S],
        ] = rs.tap_failure_to_result_sequence(f)
        return ResultSequenceWrapper(tapped_f(self.core))

    def tap_failure_to_sequence(
        self, f: Callable[[_F_default_co], Sequence[object]]
    ) -> ResultSequenceWrapper[Never, _F_default_co | _S_default_co]:
        """Apply a synchronous side effect returning a sequence
        to the wrapped [trcks.Failure][] object.

        The failure is converted to a [trcks.SuccessSequence][] where
        the original failure value is repeated once per element in
        the sequence returned by the side effect.

        Wrapped [trcks.SuccessSequence][] objects are passed on without side effects.

        Args:
            f: The synchronous side effect to be applied.

        Returns:
            A new [trcks.oop.ResultSequenceWrapper][] instance with

                - a [trcks.SuccessSequence][] containing the original failure
                    repeated once per element
                    in the sequence returned by the side effect
                    if the original [trcks.ResultSequence][] is a failure, or
                - the original [trcks.SuccessSequence][] if no side effect was applied.

        Example:
            >>> from trcks.oop import ResultSequenceWrapper
            >>> def log_err(e: str) -> list[None]:
            ...     print(f"Error logged: {e}")
            ...     print(f"Alert sent: {e}")
            ...     return [None, None]
            ...
            >>> ResultSequenceWrapper.construct_failure(
            ...     "critical"
            ... ).tap_failure_to_sequence(log_err)
            Error logged: critical
            Alert sent: critical
            ResultSequenceWrapper(core=('success', ['critical', 'critical']))
            >>>
            >>> ResultSequenceWrapper.construct_successes_from_sequence(
            ...     [1, 2]
            ... ).tap_failure_to_sequence(log_err)
            ResultSequenceWrapper(core=('success', [1, 2]))
        """
        tapped_f: Callable[
            [ResultSequence[_F_default_co, _S_default_co]],
            ResultSequence[Never, _F_default_co | _S_default_co],
        ] = rs.tap_failure_to_sequence(f)
        return ResultSequenceWrapper(tapped_f(self.core))

    def tap_successes(
        self, f: Callable[[_S_default_co], object]
    ) -> ResultSequenceWrapper[_F_default_co, _S_default_co]:
        """Apply a synchronous side effect to each element in the wrapped
        [trcks.SuccessSequence][].

        Wrapped [trcks.Failure][] objects are passed on without side effects.

        Args:
            f: The synchronous side effect to be applied to each success element.

        Returns:
            A new [trcks.oop.ResultSequenceWrapper][] instance
                with the original [trcks.ResultSequence][] object,
                allowing for further method chaining.

        Example:
            >>> result_sequence_wrapper_1 = ResultSequenceWrapper.construct_failure(
            ...     "oops"
            ... ).tap_successes(lambda x: print(f"Value: {x}"))
            >>> result_sequence_wrapper_1
            ResultSequenceWrapper(core=('failure', 'oops'))
            >>> result_sequence_wrapper_2 = (
            ...     ResultSequenceWrapper.construct_successes_from_sequence([1, 2])
            ...     .tap_successes(lambda x: print(f"Value: {x}"))
            ... )
            Value: 1
            Value: 2
            >>> result_sequence_wrapper_2
            ResultSequenceWrapper(core=('success', [1, 2]))
        """
        return ResultSequenceWrapper(rs.tap_successes(f)(self.core))

    def tap_successes_to_result(
        self, f: Callable[[_S_default_co], Result[_F, object]]
    ) -> ResultSequenceWrapper[_F_default_co | _F, _S_default_co]:
        """Apply a synchronous side effect with return type [trcks.Result][]
        to each element in the wrapped [trcks.SuccessSequence][].

        Wrapped [trcks.Failure][] objects are passed on without side effects.

        Args:
            f: The synchronous side effect to be applied to each success element.

        Returns:
            A new [trcks.oop.ResultSequenceWrapper][] instance with

                - *the original* [trcks.Failure][] if no side effect was applied,
                - *the returned* [trcks.Failure][]
                    if the applied side effect returns a [trcks.Failure][] and
                - *the original* [trcks.SuccessSequence][]
                    if the applied side effect returns [trcks.Success][]
                    for all elements.

        Example:
            >>> from trcks import Result
            >>> from trcks.oop import ResultSequenceWrapper
            >>> def audit(x: int) -> Result[str, None]:
            ...     if x > 0:
            ...         return "success", None
            ...     return "failure", "bad"
            ...
            >>> ResultSequenceWrapper.construct_successes_from_sequence(
            ...     [1, 2]
            ... ).tap_successes_to_result(audit)
            ResultSequenceWrapper(core=('success', [1, 2]))
            >>>
            >>> ResultSequenceWrapper.construct_successes_from_sequence(
            ...     [1, -1, 2]
            ... ).tap_successes_to_result(audit)
            ResultSequenceWrapper(core=('failure', 'bad'))
        """
        return ResultSequenceWrapper(rs.tap_successes_to_result(f)(self.core))

    def tap_successes_to_result_sequence(
        self, f: Callable[[_S_default_co], ResultSequence[_F, object]]
    ) -> ResultSequenceWrapper[_F_default_co | _F, _S_default_co]:
        """Apply a synchronous side effect with return type [trcks.ResultSequence][]
        to each element in the wrapped [trcks.SuccessSequence][].

        Wrapped [trcks.Failure][] objects are passed on without side effects.

        Args:
            f: The synchronous side effect to be applied to each success element.

        Returns:
            A new [trcks.oop.ResultSequenceWrapper][] instance with

                - *the original* [trcks.Failure][] if no side effect was applied,
                - *the returned* [trcks.Failure][]
                    if the applied side effect returns a [trcks.Failure][] and
                - *the original* [trcks.SuccessSequence][] element repeated once
                    per element in the side effect output if the applied side effect
                    returns [trcks.SuccessSequence][] for all elements.

        Example:
            >>> from trcks import ResultSequence
            >>> from trcks.oop import ResultSequenceWrapper
            >>> def audit(x: int) -> ResultSequence[str, None]:
            ...     if x > 0:
            ...         return "success", [None, None]
            ...     return "failure", "bad"
            ...
            >>> ResultSequenceWrapper.construct_successes(
            ...     7
            ... ).tap_successes_to_result_sequence(audit)
            ResultSequenceWrapper(core=('success', [7, 7]))
            >>>
            >>> ResultSequenceWrapper.construct_successes_from_sequence(
            ...     [1, -1]
            ... ).tap_successes_to_result_sequence(audit)
            ResultSequenceWrapper(core=('failure', 'bad'))
        """
        return ResultSequenceWrapper(rs.tap_successes_to_result_sequence(f)(self.core))

    def tap_successes_to_sequence(
        self, f: Callable[[_S_default_co], Sequence[object]]
    ) -> ResultSequenceWrapper[_F_default_co, _S_default_co]:
        """Apply a synchronous side effect returning a sequence
        to each element in the wrapped [trcks.SuccessSequence][].

        The original success elements are repeated once per element
        in the sequence returned by the side effect.

        Wrapped [trcks.Failure][] objects are passed on without side effects.

        Args:
            f: The synchronous side effect to be applied to each success element.

        Returns:
            A new [trcks.oop.ResultSequenceWrapper][] instance with

                - the original [trcks.Failure][] if no side effect was applied, or
                - a [trcks.SuccessSequence][] where each original element is repeated
                    once per element in the sequence returned by the side effect.

        Example:
            >>> from trcks.oop import ResultSequenceWrapper
            >>> def log_mult(x: int) -> list[None]:
            ...     print(f"v={x}")
            ...     print(f"v={x}")
            ...     return [None, None]
            ...
            >>> ResultSequenceWrapper.construct_successes(7).tap_successes_to_sequence(
            ...     log_mult
            ... )
            v=7
            v=7
            ResultSequenceWrapper(core=('success', [7, 7]))
        """
        return ResultSequenceWrapper(rs.tap_successes_to_sequence(f)(self.core))


class SequenceWrapper(_Wrapper[Sequence[_T_co]]):
    """Type-safe and immutable wrapper for [collections.abc.Sequence][] objects.

    The wrapped [collections.abc.Sequence][] can be accessed
    via the attribute `trcks.oop.SequenceWrapper.core`.
    The `trcks.oop.SequenceWrapper.map*` methods allow method chaining.
    The `trcks.oop.SequenceWrapper.tap*` methods allow for side effects
    without changing the wrapped sequence.

    Example:
        >>> from trcks.oop import SequenceWrapper
        >>> def double(x: int) -> int:
        ...     return x * 2
        ...
        >>> sequence_wrapper = (
        ...     SequenceWrapper
        ...     .construct_from_sequence((1, 2, 3))
        ...     .map(double)
        ...     .tap(lambda x: print(f"Processing: {x}"))
        ... )
        Processing: 2
        Processing: 4
        Processing: 6
        >>> sequence_wrapper
        SequenceWrapper(core=[2, 4, 6])
    """

    @staticmethod
    def construct(value: _T) -> SequenceWrapper[_T]:
        """Construct and wrap a [collections.abc.Sequence][] from a single value.

        Args:
            value: The value to be wrapped in a [collections.abc.Sequence][].

        Returns:
            A new [trcks.oop.SequenceWrapper][] instance with
                a [collections.abc.Sequence][] containing the single value.

        Example:
            >>> from trcks.oop import SequenceWrapper
            >>> sequence_wrapper = SequenceWrapper.construct(42)
            >>> sequence_wrapper
            SequenceWrapper(core=[42])
        """
        return SequenceWrapper(s.construct(value))

    @staticmethod
    def construct_from_sequence(seq: Sequence[_T]) -> SequenceWrapper[_T]:
        """Wrap a [collections.abc.Sequence][] object.

        Args:
            seq: The [collections.abc.Sequence][] to be wrapped.

        Returns:
            A new [trcks.oop.SequenceWrapper][] instance with
                the wrapped [collections.abc.Sequence][].

        Example:
            >>> from trcks.oop import SequenceWrapper
            >>> sequence_wrapper = SequenceWrapper.construct_from_sequence([1, 2, 3])
            >>> sequence_wrapper
            SequenceWrapper(core=[1, 2, 3])
        """
        return SequenceWrapper(seq)

    def map(self, f: Callable[[_T_co], _T]) -> SequenceWrapper[_T]:
        """Apply a synchronous function to each element in the wrapped
        [collections.abc.Sequence][].

        Args:
            f: The synchronous function to be applied to each element.

        Returns:
            A new [trcks.oop.SequenceWrapper][] instance with
                a [collections.abc.Sequence][] containing
                the results of applying the function to each element.

        Example:
            >>> from trcks.oop import SequenceWrapper
            >>> def triple(x: int) -> int:
            ...     return x * 3
            ...
            >>> sequence_wrapper = (
            ...     SequenceWrapper
            ...     .construct_from_sequence((1, 2, 3))
            ...     .map(triple)
            ... )
            >>> sequence_wrapper
            SequenceWrapper(core=[3, 6, 9])
        """
        return SequenceWrapper(s.map_(f)(self.core))

    def map_to_awaitable(
        self, f: Callable[[_T_co], Awaitable[_T]]
    ) -> AwaitableSequenceWrapper[_T]:
        """Apply an asynchronous function to each element in the wrapped
        [collections.abc.Sequence][].

        Args:
            f: The asynchronous function to be applied to each element.

        Returns:
            An [trcks.oop.AwaitableSequenceWrapper][] instance with
                an awaitable [collections.abc.Sequence][] containing
                the results of applying the function to each element.

        Example:
            >>> import asyncio
            >>> from collections.abc import Sequence
            >>> from trcks.oop import SequenceWrapper
            >>> async def add_one(x: int) -> int:
            ...     await asyncio.sleep(0.001)
            ...     return x + 1
            ...
            >>> async def main() -> Sequence[int]:
            ...     return await (
            ...         SequenceWrapper
            ...         .construct_from_sequence((1, 2, 3))
            ...         .map_to_awaitable(add_one)
            ...         .core_as_coroutine
            ...     )
            ...
            >>> asyncio.run(main())
            [2, 3, 4]
        """
        return AwaitableSequenceWrapper.construct_from_sequence(
            self.core
        ).map_to_awaitable(f)

    def map_to_awaitable_sequence(
        self, f: Callable[[_T_co], AwaitableSequence[_T]]
    ) -> AwaitableSequenceWrapper[_T]:
        """Apply an asynchronous function returning a [collections.abc.Sequence][]
        to each element in the wrapped [collections.abc.Sequence][] and flatten.

        Args:
            f: The asynchronous function to be applied to each element,
                returning an awaitable [collections.abc.Sequence][].

        Returns:
            An [trcks.oop.AwaitableSequenceWrapper][] instance with
                the flattened awaitable [collections.abc.Sequence][].

        Example:
            >>> import asyncio
            >>> from collections.abc import Sequence
            >>> from trcks.oop import SequenceWrapper
            >>> async def duplicate(x: int) -> list[int]:
            ...     await asyncio.sleep(0.001)
            ...     return [x, x]
            ...
            >>> async def main() -> Sequence[int]:
            ...     return await (
            ...         SequenceWrapper
            ...         .construct_from_sequence((1, 2))
            ...         .map_to_awaitable_sequence(duplicate)
            ...         .core_as_coroutine
            ...     )
            ...
            >>> asyncio.run(main())
            [1, 1, 2, 2]
        """
        return AwaitableSequenceWrapper.construct_from_sequence(
            self.core
        ).map_to_awaitable_sequence(f)

    def map_to_result(
        self, f: Callable[[_T_co], Result[_F, _S]]
    ) -> ResultSequenceWrapper[_F, _S]:
        """Apply a synchronous function with return type [trcks.Result][]
        to each element in the wrapped [collections.abc.Sequence][].

        Args:
            f: The synchronous function to be applied to each element.

        Returns:
            A [trcks.oop.ResultSequenceWrapper][] instance with

                - the first [trcks.Failure][] returned by the function, or
                - a [trcks.SuccessSequence][] with all transformed elements if
                    the function returns [trcks.Success][] for all elements.

        Example:
            >>> from trcks import Result
            >>> from trcks.oop import SequenceWrapper
            >>> def check(x: int) -> Result[str, int]:
            ...     if x > 0:
            ...         return "success", x * 2
            ...     return "failure", "bad"
            ...
            >>> SequenceWrapper.construct_from_sequence(
            ...     [1, 2, 3]
            ... ).map_to_result(check)
            ResultSequenceWrapper(core=('success', [2, 4, 6]))
            >>>
            >>> SequenceWrapper.construct_from_sequence(
            ...     [1, -1, 2]
            ... ).map_to_result(check)
            ResultSequenceWrapper(core=('failure', 'bad'))
        """
        return ResultSequenceWrapper.construct_successes_from_sequence(
            self.core
        ).map_successes_to_result(f)

    def map_to_result_sequence(
        self, f: Callable[[_T_co], ResultSequence[_F, _S]]
    ) -> ResultSequenceWrapper[_F, _S]:
        """Apply a synchronous function with return type [trcks.ResultSequence][]
        to each element in the wrapped [collections.abc.Sequence][] and flatten.

        Args:
            f: The synchronous function to be applied to each element,
                returning a [trcks.ResultSequence][].

        Returns:
            A [trcks.oop.ResultSequenceWrapper][] instance with

                - the first [trcks.Failure][] returned by the function, or
                - a flattened [trcks.SuccessSequence][] if
                    the function returns [trcks.SuccessSequence][] for all elements.

        Example:
            >>> from trcks import ResultSequence
            >>> from trcks.oop import SequenceWrapper
            >>> def expand(x: int) -> ResultSequence[str, int]:
            ...     if x > 0:
            ...         return "success", [x, -x]
            ...     return "failure", "bad"
            ...
            >>> SequenceWrapper.construct_from_sequence(
            ...     [1, 2]
            ... ).map_to_result_sequence(expand)
            ResultSequenceWrapper(core=('success', [1, -1, 2, -2]))
            >>>
            >>> SequenceWrapper.construct_from_sequence(
            ...     [1, -1, 2]
            ... ).map_to_result_sequence(expand)
            ResultSequenceWrapper(core=('failure', 'bad'))
        """
        return ResultSequenceWrapper.construct_successes_from_sequence(
            self.core
        ).map_successes_to_result_sequence(f)

    def map_to_sequence(
        self, f: Callable[[_T_co], Sequence[_T]]
    ) -> SequenceWrapper[_T]:
        """Apply a function returning a [collections.abc.Sequence][] to each element
        in the wrapped [collections.abc.Sequence][] and flatten the result.

        Args:
            f: The function to be applied to each element,
                returning a [collections.abc.Sequence][].

        Returns:
            A new [trcks.oop.SequenceWrapper][] instance with
                the flattened [collections.abc.Sequence][].

        Example:
            >>> from trcks.oop import SequenceWrapper
            >>> def duplicate(x: int) -> list[int]:
            ...     return [x, x]
            ...
            >>> sequence_wrapper = (
            ...     SequenceWrapper
            ...     .construct_from_sequence((1, 2, 3))
            ...     .map_to_sequence(duplicate)
            ... )
            >>> sequence_wrapper
            SequenceWrapper(core=[1, 1, 2, 2, 3, 3])
        """
        return SequenceWrapper(s.map_to_sequence(f)(self.core))

    def tap(self, f: Callable[[_T_co], object]) -> SequenceWrapper[_T_co]:
        """Apply a synchronous side effect to each element in the wrapped
        [collections.abc.Sequence][].

        Args:
            f: The synchronous side effect to be applied to each element.

        Returns:
            A new [trcks.oop.SequenceWrapper][] instance with
                the original [collections.abc.Sequence][].

        Example:
            >>> from trcks.oop import SequenceWrapper
            >>> sequence_wrapper = (
            ...     SequenceWrapper
            ...     .construct_from_sequence((1, 2, 3))
            ...     .tap(lambda x: print(f"Value: {x}"))
            ... )
            Value: 1
            Value: 2
            Value: 3
            >>> sequence_wrapper
            SequenceWrapper(core=[1, 2, 3])
        """
        return SequenceWrapper(s.tap(f)(self.core))

    def tap_to_awaitable(
        self, f: Callable[[_T_co], Awaitable[object]]
    ) -> AwaitableSequenceWrapper[_T_co]:
        """Apply an asynchronous side effect to each element in the wrapped
        [collections.abc.Sequence][].

        Args:
            f: The asynchronous side effect to be applied to each element.

        Returns:
            An [trcks.oop.AwaitableSequenceWrapper][] instance with
                the original awaitable [collections.abc.Sequence][].

        Example:
            >>> import asyncio
            >>> from collections.abc import Sequence
            >>> from trcks.oop import SequenceWrapper
            >>> async def print_value(x: int) -> None:
            ...     await asyncio.sleep(0.001)
            ...     print(f"Value: {x}")
            ...
            >>> async def main() -> Sequence[int]:
            ...     return await (
            ...         SequenceWrapper
            ...         .construct_from_sequence((1, 2, 3))
            ...         .tap_to_awaitable(print_value)
            ...         .core_as_coroutine
            ...     )
            ...
            >>> asyncio.run(main())
            Value: 1
            Value: 2
            Value: 3
            [1, 2, 3]
        """
        return AwaitableSequenceWrapper.construct_from_sequence(
            self.core
        ).tap_to_awaitable(f)

    def tap_to_awaitable_sequence(
        self, f: Callable[[_T_co], AwaitableSequence[object]]
    ) -> AwaitableSequenceWrapper[_T_co]:
        """Apply an asynchronous side effect returning a [collections.abc.Sequence][]
        to each element in the wrapped [collections.abc.Sequence][].

        Args:
            f: The asynchronous side effect to be applied to each element,
                returning an awaitable [collections.abc.Sequence][].

        Returns:
            An [trcks.oop.AwaitableSequenceWrapper][] instance with
                the original awaitable [collections.abc.Sequence][].

        Example:
            >>> import asyncio
            >>> from collections.abc import Sequence
            >>> from trcks.oop import SequenceWrapper
            >>> async def write_to_disk(x: int) -> list[str]:
            ...     await asyncio.sleep(0.001)
            ...     print(f"Wrote {x} to disk.")
            ...     return [str(x), str(x)]
            ...
            >>> async def main() -> Sequence[int]:
            ...     return await (
            ...         SequenceWrapper
            ...         .construct_from_sequence((1, 2, 3))
            ...         .tap_to_awaitable_sequence(write_to_disk)
            ...         .core_as_coroutine
            ...     )
            ...
            >>> asyncio.run(main())
            Wrote 1 to disk.
            Wrote 2 to disk.
            Wrote 3 to disk.
            [1, 1, 2, 2, 3, 3]
        """
        return AwaitableSequenceWrapper.construct_from_sequence(
            self.core
        ).tap_to_awaitable_sequence(f)

    def tap_to_result(
        self, f: Callable[[_T_co], Result[_F, object]]
    ) -> ResultSequenceWrapper[_F, _T_co]:
        """Apply a synchronous side effect with return type [trcks.Result][]
        to each element in the wrapped [collections.abc.Sequence][].

        Args:
            f: The synchronous side effect to be applied to each element.

        Returns:
            A [trcks.oop.ResultSequenceWrapper][] instance with

                - *the returned* [trcks.Failure][]
                    if the applied side effect returns a [trcks.Failure][] or
                - *the original* [trcks.SuccessSequence][]
                    if the applied side effect returns [trcks.Success][]
                    for all elements.

        Example:
            >>> from trcks import Result
            >>> from trcks.oop import SequenceWrapper
            >>> def audit(x: int) -> Result[str, None]:
            ...     if x > 0:
            ...         return "success", None
            ...     return "failure", "bad"
            ...
            >>> SequenceWrapper.construct_from_sequence(
            ...     [1, 2]
            ... ).tap_to_result(audit)
            ResultSequenceWrapper(core=('success', [1, 2]))
            >>>
            >>> SequenceWrapper.construct_from_sequence(
            ...     [1, -1, 2]
            ... ).tap_to_result(audit)
            ResultSequenceWrapper(core=('failure', 'bad'))
        """
        return ResultSequenceWrapper.construct_successes_from_sequence(
            self.core
        ).tap_successes_to_result(f)

    def tap_to_result_sequence(
        self, f: Callable[[_T_co], ResultSequence[_F, object]]
    ) -> ResultSequenceWrapper[_F, _T_co]:
        """Apply a synchronous side effect with return type [trcks.ResultSequence][]
        to each element in the wrapped [collections.abc.Sequence][].

        Args:
            f: The synchronous side effect to be applied to each element.

        Returns:
            A [trcks.oop.ResultSequenceWrapper][] instance with

                - *the returned* [trcks.Failure][]
                    if the applied side effect returns a [trcks.Failure][] or
                - *the original* [trcks.SuccessSequence][] element repeated once
                    per element in the side effect output if the applied side effect
                    returns [trcks.SuccessSequence][] for all elements.

        Example:
            >>> from trcks import ResultSequence
            >>> from trcks.oop import SequenceWrapper
            >>> def audit(x: int) -> ResultSequence[str, None]:
            ...     if x > 0:
            ...         return "success", [None, None]
            ...     return "failure", "bad"
            ...
            >>> SequenceWrapper.construct_from_sequence(
            ...     [7]
            ... ).tap_to_result_sequence(audit)
            ResultSequenceWrapper(core=('success', [7, 7]))
            >>>
            >>> SequenceWrapper.construct_from_sequence(
            ...     [1, -1]
            ... ).tap_to_result_sequence(audit)
            ResultSequenceWrapper(core=('failure', 'bad'))
        """
        return ResultSequenceWrapper.construct_successes_from_sequence(
            self.core
        ).tap_successes_to_result_sequence(f)

    def tap_to_sequence(
        self, f: Callable[[_T_co], Sequence[object]]
    ) -> SequenceWrapper[_T_co]:
        """Apply a side effect returning a [collections.abc.Sequence][] to each element
        in the wrapped [collections.abc.Sequence][].

        Args:
            f: The side effect to be applied to each element,
                returning a [collections.abc.Sequence][].

        Returns:
            A new [trcks.oop.SequenceWrapper][] instance with
                the original [collections.abc.Sequence][].

        Example:
            >>> from trcks.oop import SequenceWrapper
            >>> def write_to_disk(x: int) -> list[str]:
            ...     print(f"Wrote {x} to disk.")
            ...     return [str(x), str(x)]
            ...
            >>> sequence_wrapper = (
            ...     SequenceWrapper
            ...     .construct_from_sequence((1, 2, 3))
            ...     .tap_to_sequence(write_to_disk)
            ... )
            Wrote 1 to disk.
            Wrote 2 to disk.
            Wrote 3 to disk.
            >>> sequence_wrapper
            SequenceWrapper(core=[1, 1, 2, 2, 3, 3])
        """
        return SequenceWrapper(s.tap_to_sequence(f)(self.core))


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

    def map_to_awaitable_sequence(
        self, f: Callable[[_T_co], AwaitableSequence[_T]]
    ) -> AwaitableSequenceWrapper[_T]:
        """Apply an asynchronous function returning a [collections.abc.Sequence][]
        to the wrapped object.

        Args:
            f: The asynchronous function to be applied, returning a
                [collections.abc.Sequence][].

        Returns:
            A [trcks.oop.AwaitableSequenceWrapper][] instance with
                the result of the function application.

        Example:
            >>> import asyncio
            >>> from collections.abc import Sequence
            >>> from trcks.oop import Wrapper
            >>> async def duplicate(x: int) -> list[int]:
            ...     await asyncio.sleep(0.001)
            ...     return [x, x]
            ...
            >>> async def main() -> Sequence[int]:
            ...     awaitable_sequence_wrapper = (
            ...         Wrapper.construct(7).map_to_awaitable_sequence(duplicate)
            ...     )
            ...     sequence = await awaitable_sequence_wrapper.core_as_coroutine
            ...     assert len(sequence) == 2
            ...     return sequence
            ...
            >>> asyncio.run(main())
            [7, 7]
        """
        return AwaitableSequenceWrapper(f(self.core))

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
            ...     lambda x: ("success", x)
            ...     if x >= 0
            ...     else ("failure", "negative value")
            ... )
            ResultWrapper(core=('failure', 'negative value'))
        """
        return ResultWrapper(f(self.core))

    def map_to_result_sequence(
        self, f: Callable[[_T_co], ResultSequence[_F, _S]]
    ) -> ResultSequenceWrapper[_F, _S]:
        """Apply a synchronous function with return type [trcks.ResultSequence][]
        to the wrapped object.

        Args:
            f: The synchronous function to be applied.

        Returns:
            A [trcks.oop.ResultSequenceWrapper][] instance with
                the result of the function application.

        Example:
            >>> from trcks import ResultSequence
            >>> Wrapper.construct(-1).map_to_result_sequence(
            ...     lambda x: ("success", [x, x])
            ...     if x >= 0
            ...     else ("failure", "negative value")
            ... )
            ResultSequenceWrapper(core=('failure', 'negative value'))
        """
        return ResultSequenceWrapper(f(self.core))

    def map_to_sequence(
        self, f: Callable[[_T_co], Sequence[_T]]
    ) -> SequenceWrapper[_T]:
        """Apply a function returning a [collections.abc.Sequence][]
        to the wrapped object.

        Args:
            f: The function to be applied, returning a [collections.abc.Sequence][].

        Returns:
            A [trcks.oop.SequenceWrapper][] instance with
                the result of the function application.

        Example:
            >>> from trcks.oop import Wrapper
            >>> def duplicate(x: int) -> list[int]:
            ...     return [x, x]
            ...
            >>> Wrapper.construct(3).map_to_sequence(duplicate)
            SequenceWrapper(core=[3, 3])
        """
        return SequenceWrapper(f(self.core))

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

    def tap_to_awaitable_sequence(
        self, f: Callable[[_T_co], AwaitableSequence[object]]
    ) -> AwaitableSequenceWrapper[_T_co]:
        """Apply an asynchronous side effect returning a [collections.abc.Sequence][]
        to the wrapped object.

        Args:
            f: The asynchronous side effect to be applied,
                returning a [collections.abc.Sequence][].

        Returns:
            A [trcks.oop.AwaitableSequenceWrapper][] instance with
                the original wrapped object repeated once per item returned by the
                side effect.

        Example:
            >>> import asyncio
            >>> from trcks.oop import Wrapper
            >>> async def write_to_disk(x: int) -> list[str]:
            ...     await asyncio.sleep(0.001)
            ...     print(f"Wrote {x} to disk.")
            ...     return ["left", "right"]
            ...
            >>> awaitable_sequence_wrapper = Wrapper.construct(
            ...     3
            ... ).tap_to_awaitable_sequence(write_to_disk)
            >>> asyncio.run(awaitable_sequence_wrapper.core_as_coroutine)
            Wrote 3 to disk.
            [3, 3]
        """
        return AwaitableSequenceWrapper.construct(self.core).tap_to_awaitable_sequence(
            f
        )

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

    def tap_to_result_sequence(
        self, f: Callable[[_T_co], ResultSequence[_F, object]]
    ) -> ResultSequenceWrapper[_F, _T_co]:
        """Apply a synchronous side effect with return type [trcks.ResultSequence][]
        to the wrapped object.

        Args:
            f: The synchronous side effect to be applied.

        Returns:
            A [trcks.oop.ResultSequenceWrapper][] instance with

                - *the returned* [trcks.Failure][]
                    if the given side effect returns a [trcks.Failure][] or
                - *the original* [trcks.SuccessSequence][] element repeated once
                    per element in the side effect output if the given side effect
                    returns [trcks.SuccessSequence][].

        Example:
            >>> from trcks import ResultSequence
            >>> from trcks.oop import Wrapper
            >>> def print_positive_float(x: float) -> ResultSequence[str, None]:
            ...     if x <= 0:
            ...         return "failure", "not positive"
            ...     return (
            ...         "success",
            ...         [print(f"Positive float: {x}"), print(f"Positive float: {x}")]
            ...     )
            >>> result_sequence_wrapper_1 = Wrapper.construct(
            ...     -2.3
            ... ).tap_to_result_sequence(print_positive_float)
            >>> result_sequence_wrapper_1
            ResultSequenceWrapper(core=('failure', 'not positive'))
            >>> result_sequence_wrapper_2 = Wrapper.construct(
            ...     3.5
            ... ).tap_to_result_sequence(print_positive_float)
            Positive float: 3.5
            Positive float: 3.5
            >>> result_sequence_wrapper_2
            ResultSequenceWrapper(core=('success', [3.5, 3.5]))
        """
        return ResultSequenceWrapper.construct_successes(
            self.core
        ).tap_successes_to_result_sequence(f)

    def tap_to_sequence(
        self, f: Callable[[_T_co], Sequence[object]]
    ) -> SequenceWrapper[_T_co]:
        """Apply a side effect returning a [collections.abc.Sequence][] to the
        wrapped object.

        Args:
            f: The side effect to be applied, returning a
                [collections.abc.Sequence][].

        Returns:
            A [trcks.oop.SequenceWrapper][] instance with the original wrapped
                object repeated once per item returned by the side effect.

        Example:
            >>> from trcks.oop import Wrapper
            >>> def write_to_disk(x: int) -> list[str]:
            ...     print(f"Wrote {x} to disk.")
            ...     return ["left", "right"]
            ...
            >>> Wrapper.construct(3).tap_to_sequence(write_to_disk)
            Wrote 3 to disk.
            SequenceWrapper(core=[3, 3])
        """
        return SequenceWrapper.construct(self.core).tap_to_sequence(f)
