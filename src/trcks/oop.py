"""Object-oriented interface for `trcks`.

This module provides wrapper classes for processing values of the following types
in a method-chaining style:

- `collections.abc.Awaitable`
- `trcks.AwaitableResult`
- `trcks.Result`

Example:
    This example uses the classes `Wrapper` and `ResultWrapper`
    to create and further process a value of type `trcks.Result`:

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
    - https://en.wikipedia.org/w/index.php?title=Method_chaining&oldid=1262555147
    - https://www.geeksforgeeks.org/method-chaining-in-python/
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Generic, Literal

from trcks import AwaitableResult, Result
from trcks._typing import Never, TypeVar, override
from trcks.fp.monads import awaitable as a
from trcks.fp.monads import awaitable_result as ar
from trcks.fp.monads import identity as i
from trcks.fp.monads import result as r

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
    """Base class for all wrappers in the `trcks.oop` module.

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
    """Base class for all asynchronous wrappers in the `trcks.oop` module."""

    @property
    async def core_as_coroutine(self) -> _T_co:
        """The wrapped `collections.abc.Awaitable` object transformed into a coroutine.

        This is useful for functions that expect a coroutine (e.g. `asyncio.run`).

        Note:
            The attribute `_AwaitableWrapper.core`
            has type `collections.abc.Awaitable`,
            a superclass of `collections.abc.Coroutine`.
        """
        return await self.core


class AwaitableResultWrapper(_AwaitableWrapper[Result[_F_default_co, _S_default_co]]):
    """Typesafe and immutable wrapper for `trcks.AwaitableResult` objects.

    The wrapped object can be accessed via the attribute `AwaitableResultWrapper.core`.
    The ``AwaitableResultWrapper.map*`` methods allow method chaining.

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
        """Construct and wrap an awaitable `trcks.Failure` object from a value.

        Args:
            value: The value to be wrapped.

        Returns:
            A new `AwaitableResultWrapper` instance with
            the wrapped `trcks.AwaitableResult` object.

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
        """Construct and wrap an awaitable `trcks.Failure` from an awaitable value.

        Args:
            awtbl: The awaitable value to be wrapped.

        Returns:
            A new `AwaitableResultWrapper` instance with
            the wrapped `trcks.AwaitableResult` object.

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
        """Wrap an awaitable `trcks.Result` object.

        Args:
            a_rslt: The awaitable `trcks.Result` object to be wrapped.

        Returns:
            A new `AwaitableResultWrapper` instance with
            the wrapped `trcks.AwaitableResult` object.

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
        """Construct and wrap an awaitable `trcks.Result` object
        from a `trcks.Result` object.

        Args:
            rslt: The `trcks.Result` object to be wrapped.

        Returns:
            A new `AwaitableResultWrapper` instance with
            the wrapped `trcks.AwaitableResult` object.

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
        """Construct and wrap an awaitable `trcks.Success` object from a value.

        Args:
            value: The value to be wrapped.

        Returns:
            A new `AwaitableResultWrapper` instance with
            the wrapped `trcks.AwaitableResult` object.

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
        """Construct and wrap an awaitable `trcks.Success` from an awaitable value.

        Args:
            awtbl: The awaitable value to be wrapped.

        Returns:
            A new `AwaitableResultWrapper` instance with
            the wrapped `trcks.AwaitableResult` object.

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
        """Apply a synchronous function to the wrapped `trcks.Failure` object.

        Wrapped `trcks.Success` objects are passed on unchanged.

        Args:
            f: The synchronous function to be applied.

        Returns:
            A new `AwaitableResultWrapper` instance with

            - the result of the function application if
              the original `trcks.AwaitableResult` is a failure, or
            - the original `trcks.AwaitableResult` object if it is a success.

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
        mapped_f = ar.map_failure(f)
        return AwaitableResultWrapper(mapped_f(self.core))

    def map_failure_to_awaitable(
        self, f: Callable[[_F_default_co], Awaitable[_F]]
    ) -> AwaitableResultWrapper[_F, _S_default_co]:
        """Apply an asynchronous function to the wrapped `trcks.Failure` object.

        Wrapped `trcks.Success` objects are passed on unchanged.

        Args:
            f: The asynchronous function to be applied.

        Returns:
            A new `AwaitableResultWrapper` instance with

            - the result of the function application if
              the original `trcks.AwaitableResult` is a failure, or
            - the original `trcks.AwaitableResult` object if it is a success.

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
        mapped_f = ar.map_failure_to_awaitable(f)
        return AwaitableResultWrapper(mapped_f(self.core))

    def map_failure_to_awaitable_result(
        self, f: Callable[[_F_default_co], AwaitableResult[_F, _S]]
    ) -> AwaitableResultWrapper[_F, _S_default_co | _S]:
        """Apply an asynchronous function with return type `trcks.Result`
        to the wrapped `trcks.Failure` object.

        Wrapped `trcks.Success` objects are passed on unchanged.

        Args:
            f: The asynchronous function to be applied.

        Returns:
            A new `AwaitableResultWrapper` instance with

            - the result of the function application if
              the original `trcks.AwaitableResult` is a failure, or
            - the original `trcks.AwaitableResult` object if it is a success.

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
        mapped_f = ar.map_failure_to_awaitable_result(f)
        return AwaitableResultWrapper(mapped_f(self.core))

    def map_failure_to_result(
        self, f: Callable[[_F_default_co], Result[_F, _S]]
    ) -> AwaitableResultWrapper[_F, _S_default_co | _S]:
        """Apply a synchronous function with return type `trcks.Result`
        to the wrapped `trcks.Failure` object.

        Wrapped `trcks.Success` objects are passed on unchanged.

        Args:
            f: The synchronous function to be applied.

        Returns:
            A new `AwaitableResultWrapper` instance with

            - the result of the function application if
              the original `trcks.AwaitableResult` is a failure, or
            - the original `trcks.AwaitableResult` object if it is a success.

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
        mapped_f = ar.map_failure_to_result(f)
        return AwaitableResultWrapper(mapped_f(self.core))

    def map_success(
        self, f: Callable[[_S_default_co], _S]
    ) -> AwaitableResultWrapper[_F_default_co, _S]:
        """Apply a synchronous function to the wrapped `trcks.Success` object.

        Wrapped `trcks.Failure` objects are passed on unchanged.

        Args:
            f: The synchronous function to be applied.

        Returns:
            A new `AwaitableResultWrapper` instance with

            - the original `trcks.AwaitableResult` object if it is a failure, or
            - the result of the function application if
              the original `trcks.AwaitableResult` is a success.

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
        mapped_f = ar.map_success(f)
        return AwaitableResultWrapper(mapped_f(self.core))

    def map_success_to_awaitable(
        self, f: Callable[[_S_default_co], Awaitable[_S]]
    ) -> AwaitableResultWrapper[_F_default_co, _S]:
        """Apply an asynchronous function to the wrapped `trcks.Success` object.

        Wrapped `trcks.Failure` objects are passed on unchanged.

        Args:
            f: The asynchronous function to be applied.

        Returns:
            A new `AwaitableResultWrapper` instance with

            - the original `trcks.AwaitableResult` object if it is a failure, or
            - the result of the function application if
              the original `trcks.AwaitableResult` is a success.

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
        mapped_f = ar.map_success_to_awaitable(f)
        return AwaitableResultWrapper(mapped_f(self.core))

    def map_success_to_awaitable_result(
        self, f: Callable[[_S_default_co], AwaitableResult[_F, _S]]
    ) -> AwaitableResultWrapper[_F_default_co | _F, _S]:
        """Apply an asynchronous function with return type `trcks.Result`
        to the wrapped `trcks.Success` object.

        Wrapped `trcks.Failure` objects are passed on unchanged.

        Args:
            f: The asynchronous function to be applied.

        Returns:
            A new `AwaitableResultWrapper` instance with

            - the original `trcks.AwaitableResult` object if it is a failure, or
            - the result of the function application if
              the original `trcks.AwaitableResult` is a success.

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
        mapped_f = ar.map_success_to_awaitable_result(f)
        return AwaitableResultWrapper(mapped_f(self.core))

    def map_success_to_result(
        self, f: Callable[[_S_default_co], Result[_F, _S]]
    ) -> AwaitableResultWrapper[_F_default_co | _F, _S]:
        """Apply a synchronous function with return type `trcks.Result`
        to the wrapped `trcks.Success` object.

        Wrapped `trcks.Failure` objects are passed on unchanged.

        Args:
            f: The synchronous function to be applied.

        Returns:
            A new `AwaitableResultWrapper` instance with

            - the original `trcks.AwaitableResult` object if it is a failure, or
            - the result of the function application if
              the original `trcks.AwaitableResult` is a success.

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
        mapped_f = ar.map_success_to_result(f)
        return AwaitableResultWrapper(mapped_f(self.core))

    def tap_failure(
        self, f: Callable[[_F_default_co], object]
    ) -> AwaitableResultWrapper[_F_default_co, _S_default_co]:
        """Apply a synchronous side effect to the wrapped `trcks.Failure` object.

        Wrapped `trcks.Success` objects are passed on without side effects.

        Args:
            f: The synchronous side effect to be applied.

        Returns:
            A new `AwaitableResultWrapper` instance
            with the original `trcks.Result` object,
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
        tapped_f = ar.tap_failure(f)
        return AwaitableResultWrapper(tapped_f(self.core))

    def tap_failure_to_awaitable(
        self, f: Callable[[_F_default_co], Awaitable[object]]
    ) -> AwaitableResultWrapper[_F_default_co, _S_default_co]:
        """Apply an asynchronous side effect to the wrapped `trcks.Failure` object.

        Wrapped `trcks.Success` objects are passed on without side effects.

        Args:
            f: The asynchronous side effect to be applied.

        Returns:
            A new `AwaitableResultWrapper` instance
            with the original `trcks.Result` object,
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
        tapped_f = ar.tap_failure_to_awaitable(f)
        return AwaitableResultWrapper(tapped_f(self.core))

    def tap_failure_to_awaitable_result(
        self, f: Callable[[_F_default_co], AwaitableResult[object, _S]]
    ) -> AwaitableResultWrapper[_F_default_co, _S_default_co | _S]:
        """Apply an asynchronous side effect with return type `trcks.Result`
        to the wrapped `trcks.Failure` object.

        Wrapped `trcks.Success` objects are passed on without side effects.

        Args:
            f: The asynchronous side effect to be applied.

        Returns:
            A new `AwaitableResultWrapper` instance with

            - *the original* `trcks.Failure`
              if the applied side effect returns a `trcks.Failure`,
            - *the returned* `trcks.Success`
              if the applied side effect returns a `trcks.Success` and
            - *the original* `trcks.Success` if no side effect was applied.
        """
        tapped_f = ar.tap_failure_to_awaitable_result(f)
        return AwaitableResultWrapper(tapped_f(self.core))

    def tap_failure_to_result(
        self, f: Callable[[_F_default_co], Result[object, _S]]
    ) -> AwaitableResultWrapper[_F_default_co, _S_default_co | _S]:
        """Apply a synchronous side effect with return type `trcks.Result`
        to the wrapped `trcks.Failure` object.

        Wrapped `trcks.Success` objects are passed on without side effects.

        Args:
            f: The synchronous side effect to be applied.

        Returns:
            A new `AwaitableResultWrapper` instance with

            - *the original* `trcks.Failure`
              if the applied side effect returns a `trcks.Failure`,
            - *the returned* `trcks.Success`
              if the applied side effect returns a `trcks.Success` and
            - *the original* `trcks.Success` if no side effect was applied.

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
        tapped_f = ar.tap_failure_to_result(f)
        return AwaitableResultWrapper(tapped_f(self.core))

    def tap_success(
        self, f: Callable[[_S_default_co], object]
    ) -> AwaitableResultWrapper[_F_default_co, _S_default_co]:
        """Apply a synchronous side effect to the wrapped `trcks.Success` object.

        Wrapped `trcks.Failure` objects are passed on without side effects.

        Args:
            f: The synchronous side effect to be applied.

        Returns:
            A new `AwaitableResultWrapper` instance
            with the original `trcks.Result` object,
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
        tapped_f = ar.tap_success(f)
        return AwaitableResultWrapper(tapped_f(self.core))

    def tap_success_to_awaitable(
        self, f: Callable[[_S_default_co], Awaitable[object]]
    ) -> AwaitableResultWrapper[_F_default_co, _S_default_co]:
        """Apply an asynchronous side effect to the wrapped `trcks.Success` object.

        Wrapped `trcks.Failure` objects are passed on without side effects.

        Args:
            f: The asynchronous side effect to be applied.

        Returns:
            A new `AwaitableResultWrapper` instance
            with the original `trcks.Result` object,
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
        tapped_f = ar.tap_success_to_awaitable(f)
        return AwaitableResultWrapper(tapped_f(self.core))

    def tap_success_to_awaitable_result(
        self, f: Callable[[_S_default_co], AwaitableResult[_F, object]]
    ) -> AwaitableResultWrapper[_F_default_co | _F, _S_default_co]:
        """Apply an asynchronous side effect with return type `trcks.Result`
        to the wrapped `trcks.Success` object.

        Wrapped `trcks.Failure` objects are passed on without side effects.

        Args:
            f: The asynchronous side effect to be applied.

        Returns:
            A new `AwaitableResultWrapper` instance with

            - *the original* `trcks.Failure` if no side effect was applied,
            - *the returned* `trcks.Failure`
              if the applied side effect returns a `trcks.Failure` and
            - *the original* `trcks.Success`
              if the applied side effect returns a `trcks.Success`.

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
        tapped_f = ar.tap_success_to_awaitable_result(f)
        return AwaitableResultWrapper(tapped_f(self.core))

    def tap_success_to_result(
        self, f: Callable[[_S_default_co], Result[_F, object]]
    ) -> AwaitableResultWrapper[_F_default_co | _F, _S_default_co]:
        """Apply a synchronous side effect with return type `trcks.Result`
        to the wrapped `trcks.Success` object.

        Wrapped `trcks.Failure` objects are passed on without side effects.

        Args:
            f: The synchronous side effect to be applied.

        Returns:
            A new `AwaitableResultWrapper` instance with

            - *the original* `trcks.Failure` if no side effect was applied,
            - *the returned* `trcks.Failure`
              if the applied side effect returns a `trcks.Failure` and
            - *the original* `trcks.Success`
              if the applied side effect returns a `trcks.Success`.
        """
        tapped_f = ar.tap_success_to_result(f)
        return AwaitableResultWrapper(tapped_f(self.core))

    @property
    async def track(self) -> Literal["failure", "success"]:
        """First element of the awaited attribute `AwaitableResultWrapper.core`.

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
        """Second element of the awaited attribute `AwaitableResultWrapper.core`.

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


class AwaitableWrapper(_AwaitableWrapper[_T_co]):
    """Typesafe and immutable wrapper for `collections.abc.Awaitable` objects.

    The wrapped `collections.abc.Awaitable` can be accessed
    via the attribute `AwaitableWrapper.core`.
    The ``AwaitableWrapper.map*`` methods allow method chaining.
    The ``AwaitableWrapper.tap*`` methods allow for side effects
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
        """Apply a synchronous function
        to the wrapped `collections.abc.Awaitable` object.

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
        """Apply an asynchronous function
        to the wrapped `collections.abc.Awaitable` object.

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
        """Apply an asynchronous function with return type `trcks.Result`
        to the wrapped `collections.abc.Awaitable` object.

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

    def map_to_result(
        self, f: Callable[[_T_co], Result[_F, _S]]
    ) -> AwaitableResultWrapper[_F, _S]:
        """Apply a synchronous function with return type `trcks.Result`
        to the wrapped `collections.abc.Awaitable` object.

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

    def tap(self, f: Callable[[_T_co], object]) -> AwaitableWrapper[_T_co]:
        """Apply a synchronous side effect
        to the wrapped `collections.abc.Awaitable` object.

        Args:
            f: The synchronous side effect to be applied.

        Returns:
            A new `AwaitableWrapper` instance with
            the original `collections.abc.Awaitable` object.

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
        tapped_f = a.tap(f)
        return AwaitableWrapper(tapped_f(self.core))

    def tap_to_awaitable(
        self, f: Callable[[_T_co], Awaitable[object]]
    ) -> AwaitableWrapper[_T_co]:
        """Apply an asynchronous side effect
        to the wrapped `collections.abc.Awaitable` object.

        Args:
            f: The asynchronous side effect to be applied.

        Returns:
            An `AwaitableWrapper` instance with the original wrapped object.

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
        tapped_f = a.tap_to_awaitable(f)
        return AwaitableWrapper(tapped_f(self.core))

    def tap_to_awaitable_result(
        self, f: Callable[[_T_co], AwaitableResult[_F, object]]
    ) -> AwaitableResultWrapper[_F, _T_co]:
        """Apply an asynchronous side effect with return type `trcks.Result`
        to the wrapped object.

        Args:
            f: The asynchronous side effect to be applied.

        Returns:
            An `AwaitableResultWrapper` instance with

            - *the returned* `Failure` if the given side effect returns a `Failure` or
            - a `Success` instance containing *the original* wrapped object
              if the given side effect returns a `Success`.

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

    def tap_to_result(
        self, f: Callable[[_T_co], Result[_F, object]]
    ) -> AwaitableResultWrapper[_F, _T_co]:
        """Apply a synchronous side effect with return type `trcks.Result`
        to the wrapped object.

        Args:
            f: The synchronous side effect to be applied.

        Returns:
            An `AwaitableResultWrapper` instance with

            - *the returned* `Failure` if the given side effect returns a `Failure` or
            - a `Success` instance containing *the original* wrapped object
              if the given side effect returns a `Success`.

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


class ResultWrapper(_Wrapper[Result[_F_default_co, _S_default_co]]):
    """Typesafe and immutable wrapper for `trcks.Result` objects.

    The wrapped object can be accessed via the attribute `ResultWrapper.core`.
    The ``ResultWrapper.map*`` methods allow method chaining.
    The ``ResultWrapper.tap*`` methods allow for side effects.

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
        """Construct and wrap a `trcks.Failure` object from a value.

        Args:
            value: The value to be wrapped.

        Returns:
            A new `ResultWrapper` instance with the wrapped `trcks.Failure` object.

        Example:
            >>> ResultWrapper.construct_failure(42)
            ResultWrapper(core=('failure', 42))
        """
        return ResultWrapper(r.construct_failure(value))

    @staticmethod
    def construct_from_result(
        rslt: Result[_F_default, _S_default],
    ) -> ResultWrapper[_F_default, _S_default]:
        """Wrap a `trcks.Result` object.

        Args:
            rslt: The `trcks.Result` object to be wrapped.

        Returns:
            A new `ResultWrapper` instance with the wrapped `trcks.Result` object.

        Example:
            >>> ResultWrapper.construct_from_result(("success", 0.0))
            ResultWrapper(core=('success', 0.0))
        """
        return ResultWrapper(rslt)

    @staticmethod
    def construct_success(value: _S) -> ResultWrapper[Never, _S]:
        """Construct and wrap a `trcks.Success` object from a value.

        Args:
            value: The value to be wrapped.

        Returns:
            A new `ResultWrapper` instance with the wrapped `trcks.Success` object.

        Example:
            >>> ResultWrapper.construct_success(42)
            ResultWrapper(core=('success', 42))
        """
        return ResultWrapper(r.construct_success(value))

    def map_failure(
        self, f: Callable[[_F_default_co], _F]
    ) -> ResultWrapper[_F, _S_default_co]:
        """Apply a synchronous function to the wrapped `trcks.Failure` object.

        Wrapped `trcks.Success` objects are passed on unchanged.

        Args:
            f: The synchronous function to be applied.

        Returns:
            A new `ResultWrapper` instance with

            - the result of the function application if
              the original `trcks.Result` is a failure, or
            - the original `trcks.Result` object if it is a success.

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
        mapped_f = r.map_failure(f)
        return ResultWrapper(mapped_f(self.core))

    def map_failure_to_awaitable(
        self, f: Callable[[_F_default_co], Awaitable[_F]]
    ) -> AwaitableResultWrapper[_F, _S_default_co]:
        """Apply an asynchronous function to the wrapped `trcks.Failure` object.

        Wrapped `trcks.Success` objects are passed on unchanged.

        Args:
            f: The asynchronous function to be applied.

        Returns:
            An `AwaitableResultWrapper` instance with

            - the result of the function application if
              the original `trcks.Result` is a failure, or
            - the original `trcks.Result` object if it is a success.

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
        """Apply an asynchronous function with return type `trcks.Result`
        to the wrapped `trcks.Failure` object.

        Wrapped `trcks.Success` objects are passed on unchanged.

        Args:
            f: The asynchronous function to be applied.

        Returns:
            An `AwaitableResultWrapper` instance with

            - the result of the function application if
              the original `trcks.Result` is a failure, or
            - the original `trcks.Result` object if it is a success.

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
        """Apply a synchronous function with return type `trcks.Result`
        to the wrapped `trcks.Failure` object.

        Wrapped `trcks.Success` objects are passed on unchanged.

        Args:
            f: The synchronous function to be applied.

        Returns:
            A new `ResultWrapper` instance with

            - the result of the function application if
              the original `trcks.Result` is a failure, or
            - the original `trcks.Result` object if it is a success.

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
        mapped_f = r.map_failure_to_result(f)
        return ResultWrapper(mapped_f(self.core))

    def map_success(
        self, f: Callable[[_S_default_co], _S]
    ) -> ResultWrapper[_F_default_co, _S]:
        """Apply a synchronous function to the wrapped `trcks.Success` object.

        Wrapped `trcks.Failure` objects are passed on unchanged.

        Args:
            f: The synchronous function to be applied.

        Returns:
            A new `ResultWrapper` instance with

            - the original `trcks.Result` object if it is a failure, or
            - the result of the function application if
              the original `trcks.Result` is a success.

        Example:
            >>> ResultWrapper.construct_failure("not found").map_success(lambda n: n+1)
            ResultWrapper(core=('failure', 'not found'))
            >>>
            >>> ResultWrapper.construct_success(42).map_success(lambda n: n+1)
            ResultWrapper(core=('success', 43))
        """
        mapped_f = r.map_success(f)
        return ResultWrapper(mapped_f(self.core))

    def map_success_to_awaitable(
        self, f: Callable[[_S_default_co], Awaitable[_S]]
    ) -> AwaitableResultWrapper[_F_default_co, _S]:
        """Apply an asynchronous function to the wrapped `trcks.Success` object.

        Wrapped `trcks.Failure` objects are passed on unchanged.

        Args:
            f: The asynchronous function to be applied.

        Returns:
            An `AwaitableResultWrapper` instance with

            - the original `trcks.Result` object if it is a failure, or
            - the result of the function application if
              the original `trcks.Result` is a success.

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
        """Apply an asynchronous function with return type `trcks.Result`
        to the wrapped `trcks.Success` object.

        Wrapped `trcks.Failure` objects are passed on unchanged.

        Args:
            f: The asynchronous function to be applied.

        Returns:
            An `AwaitableResultWrapper` instance with

            - the original `trcks.Result` object if it is a failure, or
            - the result of the function application if
              the original `trcks.Result` is a success.

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
        """Apply a synchronous function with return type `trcks.Result`
        to the wrapped `trcks.Success` object.

        Wrapped `trcks.Failure` objects are passed on unchanged.

        Args:
            f: The synchronous function to be applied.

        Returns:
            A new `ResultWrapper` instance with

            - the original `trcks.Result` object if it is a failure, or
            - the result of the function application if
              the original `trcks.Result` is a success.

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
        mapped_f = r.map_success_to_result(f)
        return ResultWrapper(mapped_f(self.core))

    def tap_failure(
        self, f: Callable[[_F_default_co], object]
    ) -> ResultWrapper[_F_default_co, _S_default_co]:
        """Apply a synchronous side effect to the wrapped `trcks.Failure` object.

        Wrapped `trcks.Success` objects are passed on without side effects.

        Args:
            f: The synchronous side effect to be applied.

        Returns:
            A new `ResultWrapper` instance with the original `trcks.Result` object,
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
        tapped_f = r.tap_failure(f)
        return ResultWrapper(tapped_f(self.core))

    def tap_failure_to_awaitable(
        self, f: Callable[[_F_default_co], Awaitable[object]]
    ) -> AwaitableResultWrapper[_F_default_co, _S_default_co]:
        """Apply an asynchronous side effect to the wrapped `trcks.Failure` object.

        Wrapped `trcks.Success` objects are passed on without side effects.

        Args:
            f: The asynchronous side effect to be applied.

        Returns:
            An `AwaitableResultWrapper` instance
            with the original `trcks.Result` object,
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
        """Apply an asynchronous side effect with return type `trcks.Result`
        to the wrapped `trcks.Failure` object.

        Wrapped `trcks.Success` objects are passed on without side effects.

        Args:
            f: The asynchronous side effect to be applied.

        Returns:
            An `AwaitableResultWrapper` instance with

            - *the original* `trcks.Failure`
              if the applied side effect returns a `trcks.Failure`,
            - *the returned* `trcks.Success`
              if the applied side effect returns a `trcks.Success` and
            - *the original* `trcks.Success` if no side effect was applied.

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
        """Apply a synchronous side effect with return type `trcks.Result`
        to the wrapped `trcks.Failure` object.

        Wrapped `trcks.Success` objects are passed on without side effects.

        Args:
            f: The synchronous side effect to be applied.

        Returns:
            A new `ResultWrapper` instance with

            - *the original* `trcks.Failure`
              if the applied side effect returns a `trcks.Failure`,
            - *the returned* `trcks.Success`
              if the applied side effect returns a `trcks.Success` and
            - *the original* `trcks.Success` if no side effect was applied.

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
        tapped_f = r.tap_failure_to_result(f)
        return ResultWrapper(tapped_f(self.core))

    def tap_success(
        self, f: Callable[[_S_default_co], object]
    ) -> ResultWrapper[_F_default_co, _S_default_co]:
        """Apply a synchronous side effect to the wrapped `trcks.Success` object.

        Wrapped `trcks.Failure` objects are passed on without side effects.

        Args:
            f: The synchronous side effect to be applied.

        Returns:
            A new `ResultWrapper` instance with the original `trcks.Result` object,
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
        tapped_f = r.tap_success(f)
        return ResultWrapper(tapped_f(self.core))

    def tap_success_to_awaitable(
        self, f: Callable[[_S_default_co], Awaitable[object]]
    ) -> AwaitableResultWrapper[_F_default_co, _S_default_co]:
        """Apply an asynchronous side effect to the wrapped `trcks.Success` object.

        Wrapped `trcks.Failure` objects are passed on without side effects.

        Args:
            f: The asynchronous side effect to be applied.

        Returns:
            An `AwaitableResultWrapper` instance
            with the original `trcks.Result` object,
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
        """Apply an asynchronous side effect with return type `trcks.Result`
        to the wrapped `trcks.Success` object.

        Wrapped `trcks.Failure` objects are passed on without side effects.

        Args:
            f: The asynchronous side effect to be applied.

        Returns:
            An `AwaitableResultWrapper` instance with

            - *the original* `trcks.Failure` if no side effect was applied,
            - *the returned* `trcks.Failure`
              if the applied side effect returns a `trcks.Failure` and
            - *the original* `trcks.Success`
              if the applied side effect returns a `trcks.Success`.

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
        """Apply a synchronous side effect with return type `trcks.Result`
        to the wrapped `trcks.Success` object.

        Wrapped `trcks.Failure` objects are passed on without side effects.

        Args:
            f: The synchronous side effect to be applied.

        Returns:
            A new `ResultWrapper` instance with

            - *the original* `trcks.Failure` if no side effect was applied,
            - *the returned* `trcks.Failure`
              if the applied side effect returns a `trcks.Failure` and
            - *the original* `trcks.Success`
              if the applied side effect returns a `trcks.Success`.
        """
        tapped_f = r.tap_success_to_result(f)
        return ResultWrapper(tapped_f(self.core))

    @property
    def track(self) -> Literal["failure", "success"]:
        """First element of the attribute `ResultWrapper.core`.

        Example:
            >>> ResultWrapper(core=('failure', 42)).track
            'failure'
        """
        return self.core[0]

    @property
    def value(self) -> _F_default_co | _S_default_co:
        """Second element of the attribute `ResultWrapper.core`.

        Example:
            >>> ResultWrapper(core=('failure', 42)).value
            42
        """
        return self.core[1]


class Wrapper(_Wrapper[_T_co]):
    """Typesafe and immutable wrapper for arbitrary objects.

    The wrapped object can be accessed via the attribute `Wrapper.core`.
    The ``Wrapper.map*`` methods allow method chaining.
    The ``Wrapper.tap*`` methods allow for side effects
    without changing the wrapped object.

    Example:
        The string ``"Hello"`` is wrapped and manipulated in the following example.
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
        """Apply an asynchronous function with return type `trcks.Result`
        to the wrapped object.

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

    def map_to_result(
        self, f: Callable[[_T_co], Result[_F, _S]]
    ) -> ResultWrapper[_F, _S]:
        """Apply a synchronous function with return type `trcks.Result`
        to the wrapped object.

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

    def tap(self, f: Callable[[_T_co], object]) -> Wrapper[_T_co]:
        """Apply a synchronous side effect to the wrapped object.

        Args:
            f: The synchronous side effect to be applied.

        Returns:
            A new `Wrapper` instance with the original wrapped object,
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
            An `AwaitableWrapper` instance with the original wrapped object.

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
        """Apply an asynchronous side effect with return type `trcks.Result`
        to the wrapped object.

        Args:
            f: The asynchronous side effect to be applied.

        Returns:
            An `AwaitableResultWrapper` instance with

            - *the returned* `Failure` if the given side effect returns a `Failure` or
            - a `Success` instance containing *the original* wrapped object
              if the given side effect returns a `Success`.

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

    def tap_to_result(
        self, f: Callable[[_T_co], Result[_F, object]]
    ) -> ResultWrapper[_F, _T_co]:
        """Apply a synchronous side effect with return type `trcks.Result`
        to the wrapped object.

        Args:
            f: The synchronous side effect to be applied.

        Returns:
            A `ResultWrapper` instance with

            - *the returned* `Failure` if the given side effect returns a `Failure` or
            - a `Success` instance containing *the original* wrapped object
              if the given side effect returns a `Success`.

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
