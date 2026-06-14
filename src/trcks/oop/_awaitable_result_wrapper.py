from __future__ import annotations

from typing import TYPE_CHECKING

from trcks import Result
from trcks._typing import Never, TypeVar, deprecated
from trcks.fp.monads import awaitable_result as ar
from trcks.oop._awaitable_result_tuple_wrapper import AwaitableResultTupleWrapper
from trcks.oop._base_awaitable_wrapper import BaseAwaitableWrapper

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable, Iterable

    from trcks import (
        AwaitableResult,
        AwaitableResultIterable,
        AwaitableResultTuple,
        ResultIterable,
        ResultTuple,
    )

__docformat__ = "google"

_F = TypeVar("_F")
_S = TypeVar("_S")

_F_default = TypeVar("_F_default", default=Never)
_S_default = TypeVar("_S_default", default=Never)

_F_default_co = TypeVar("_F_default_co", covariant=True, default=Never)
_S_default_co = TypeVar("_S_default_co", covariant=True, default=Never)


class AwaitableResultWrapper(
    BaseAwaitableWrapper[Result[_F_default_co, _S_default_co]]
):
    """Type-safe and immutable wrapper for [trcks.AwaitableResult][] objects.

    The wrapped object can be accessed
    via the attribute [trcks.oop.BaseWrapper.core][].
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

    __slots__: tuple[str, ...] = ()

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

    def map_failure_to_awaitable_result_iterable(
        self, f: Callable[[_F_default_co], AwaitableResultIterable[_F, _S]]
    ) -> AwaitableResultTupleWrapper[_F, _S_default_co | _S]:
        """Apply an asynchronous function with return type
        [trcks.AwaitableResultIterable][] to the wrapped [trcks.Failure][] object.

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
            ...     .map_failure_to_awaitable_result_iterable(recover)
            ... )
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('success', (0.0, 1.0))
            >>>
            >>> wrapper_2 = (
            ...     AwaitableResultWrapper
            ...     .construct_success(25.0)
            ...     .map_failure_to_awaitable_result_iterable(recover)
            ... )
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('success', (25.0,))
        """
        return AwaitableResultTupleWrapper.construct_from_awaitable_result(
            self.core
        ).map_failure_to_awaitable_result_iterable(f)

    @deprecated("Use map_failure_to_awaitable_result_iterable instead")
    def map_failure_to_awaitable_result_tuple(
        self, f: Callable[[_F_default_co], AwaitableResultTuple[_F, _S]]
    ) -> AwaitableResultTupleWrapper[_F, _S_default_co | _S]:
        """Deprecated alias for
        [trcks.oop.AwaitableResultWrapper.map_failure_to_awaitable_result_iterable][].
        """
        return self.map_failure_to_awaitable_result_iterable(f)  # pragma: no cover

    def map_failure_to_iterable(
        self, f: Callable[[_F_default_co], Iterable[_S]]
    ) -> AwaitableResultTupleWrapper[Never, _S_default_co | _S]:
        """Apply a synchronous function returning an [collections.abc.Iterable][]
        to the wrapped [trcks.Failure][] object.

        The failure is converted to a [trcks.SuccessTuple][].
        Wrapped [trcks.Success][] objects are passed on unchanged.

        Args:
            f: The synchronous function to be applied,
                returning an [collections.abc.Iterable][].

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
            ...     .map_failure_to_iterable(recover)
            ... )
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('success', (0.0, 1.0))
            >>>
            >>> wrapper_2 = (
            ...     AwaitableResultWrapper
            ...     .construct_success(25.0)
            ...     .map_failure_to_iterable(recover)
            ... )
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('success', (25.0,))
        """
        return AwaitableResultTupleWrapper.construct_from_awaitable_result(
            self.core
        ).map_failure_to_iterable(f)

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

    def map_failure_to_result_iterable(
        self, f: Callable[[_F_default_co], ResultIterable[_F, _S]]
    ) -> AwaitableResultTupleWrapper[_F, _S_default_co | _S]:
        """Apply a synchronous function with return type [trcks.ResultIterable][]
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
            ...     .map_failure_to_result_iterable(recover)
            ... )
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('success', (0.0, 1.0))
            >>>
            >>> wrapper_2 = (
            ...     AwaitableResultWrapper
            ...     .construct_success(25.0)
            ...     .map_failure_to_result_iterable(recover)
            ... )
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('success', (25.0,))
        """
        return AwaitableResultTupleWrapper.construct_from_awaitable_result(
            self.core
        ).map_failure_to_result_iterable(f)

    @deprecated("Use map_failure_to_result_iterable instead")
    def map_failure_to_result_tuple(
        self, f: Callable[[_F_default_co], ResultTuple[_F, _S]]
    ) -> AwaitableResultTupleWrapper[_F, _S_default_co | _S]:
        """Deprecated alias for
        [trcks.oop.AwaitableResultWrapper.map_failure_to_result_iterable][].
        """
        return self.map_failure_to_result_iterable(f)  # pragma: no cover

    @deprecated("Use map_failure_to_iterable instead")
    def map_failure_to_tuple(
        self, f: Callable[[_F_default_co], tuple[_S, ...]]
    ) -> AwaitableResultTupleWrapper[Never, _S_default_co | _S]:
        """Deprecated alias for
        [trcks.oop.AwaitableResultWrapper.map_failure_to_iterable][].
        """
        return self.map_failure_to_iterable(f)  # pragma: no cover

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

    def map_success_to_awaitable_result_iterable(
        self, f: Callable[[_S_default_co], AwaitableResultIterable[_F, _S]]
    ) -> AwaitableResultTupleWrapper[_F_default_co | _F, _S]:
        """Apply an asynchronous function with return type
        [trcks.AwaitableResultIterable][] to the wrapped [trcks.Success][] object.

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
            ...     .map_success_to_awaitable_result_iterable(slowly_expand)
            ... )
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('failure', 'not found')
            >>>
            >>> wrapper_2 = (
            ...     AwaitableResultWrapper
            ...     .construct_success(5.0)
            ...     .map_success_to_awaitable_result_iterable(slowly_expand)
            ... )
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('success', (5.0, 10.0))
        """
        return AwaitableResultTupleWrapper.construct_from_awaitable_result(
            self.core
        ).map_successes_to_awaitable_result_iterable(f)

    @deprecated("Use map_success_to_awaitable_result_iterable instead")
    def map_success_to_awaitable_result_tuple(
        self, f: Callable[[_S_default_co], AwaitableResultTuple[_F, _S]]
    ) -> AwaitableResultTupleWrapper[_F_default_co | _F, _S]:
        """Deprecated alias for
        [trcks.oop.AwaitableResultWrapper.map_success_to_awaitable_result_iterable][].
        """
        return self.map_success_to_awaitable_result_iterable(f)  # pragma: no cover

    def map_success_to_iterable(
        self, f: Callable[[_S_default_co], Iterable[_S]]
    ) -> AwaitableResultTupleWrapper[_F_default_co, _S]:
        """Apply a synchronous function returning an [collections.abc.Iterable][]
        to the wrapped [trcks.Success][] object.

        Wrapped [trcks.Failure][] objects are passed on unchanged.

        Args:
            f: The synchronous function to be applied,
                returning an [collections.abc.Iterable][].

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
            ...     .map_success_to_iterable(duplicate)
            ... )
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('failure', 'not found')
            >>>
            >>> wrapper_2 = (
            ...     AwaitableResultWrapper
            ...     .construct_success(5.0)
            ...     .map_success_to_iterable(duplicate)
            ... )
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('success', (5.0, 5.0))
        """
        return AwaitableResultTupleWrapper.construct_from_awaitable_result(
            self.core
        ).map_successes_to_iterable(f)

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

    def map_success_to_result_iterable(
        self, f: Callable[[_S_default_co], ResultIterable[_F, _S]]
    ) -> AwaitableResultTupleWrapper[_F_default_co | _F, _S]:
        """Apply a synchronous function with return type [trcks.ResultIterable][]
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
            ...     .map_success_to_result_iterable(expand)
            ... )
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('failure', 'not found')
            >>>
            >>> wrapper_2 = (
            ...     AwaitableResultWrapper
            ...     .construct_success(5.0)
            ...     .map_success_to_result_iterable(expand)
            ... )
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('success', (5.0, 10.0))
        """
        return AwaitableResultTupleWrapper.construct_from_awaitable_result(
            self.core
        ).map_successes_to_result_iterable(f)

    @deprecated("Use map_success_to_result_iterable instead")
    def map_success_to_result_tuple(
        self, f: Callable[[_S_default_co], ResultTuple[_F, _S]]
    ) -> AwaitableResultTupleWrapper[_F_default_co | _F, _S]:
        """Deprecated alias for
        [trcks.oop.AwaitableResultWrapper.map_success_to_result_iterable][].
        """
        return self.map_success_to_result_iterable(f)  # pragma: no cover

    @deprecated("Use map_success_to_iterable instead")
    def map_success_to_tuple(
        self, f: Callable[[_S_default_co], tuple[_S, ...]]
    ) -> AwaitableResultTupleWrapper[_F_default_co, _S]:
        """Deprecated alias for
        [trcks.oop.AwaitableResultWrapper.map_success_to_iterable][].
        """
        return self.map_success_to_iterable(f)  # pragma: no cover

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

    def tap_failure_to_awaitable_result_iterable(
        self, f: Callable[[_F_default_co], AwaitableResultIterable[object, _S]]
    ) -> AwaitableResultTupleWrapper[_F_default_co, _S_default_co | _S]:
        """Apply an asynchronous side effect with return type
        [trcks.AwaitableResultIterable][] to the wrapped [trcks.Failure][] object.

        Wrapped [trcks.Success][] objects are passed on without side effects.

        Args:
            f: The asynchronous side effect to be applied.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - *the original* [trcks.Failure][]
                    if the applied side effect returns a [trcks.Failure][],
                - *the returned* [trcks.SuccessIterable][]
                    if the applied side effect returns a [trcks.SuccessIterable][]
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
            ...     .tap_failure_to_awaitable_result_iterable(recover)
            ... )
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('success', (0.0, 1.0))
            >>>
            >>> wrapper_2 = (
            ...     AwaitableResultWrapper
            ...     .construct_success(42)
            ...     .tap_failure_to_awaitable_result_iterable(recover)
            ... )
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('success', (42,))
        """
        return AwaitableResultTupleWrapper.construct_from_awaitable_result(
            self.core
        ).tap_failure_to_awaitable_result_iterable(f)

    @deprecated("Use tap_failure_to_awaitable_result_iterable instead")
    def tap_failure_to_awaitable_result_tuple(
        self, f: Callable[[_F_default_co], AwaitableResultTuple[object, _S]]
    ) -> AwaitableResultTupleWrapper[_F_default_co, _S_default_co | _S]:
        """Deprecated alias for
        [trcks.oop.AwaitableResultWrapper.tap_failure_to_awaitable_result_iterable][].
        """
        return self.tap_failure_to_awaitable_result_iterable(f)  # pragma: no cover

    def tap_failure_to_iterable(
        self, f: Callable[[_F_default_co], Iterable[object]]
    ) -> AwaitableResultTupleWrapper[Never, _F_default_co | _S_default_co]:
        """Apply a synchronous side effect returning an [collections.abc.Iterable][]
        to the wrapped [trcks.Failure][] object.

        The failure is converted to a [trcks.SuccessTuple][] where
        the original failure value is repeated once per element in
        the [collections.abc.Iterable][] returned by the side effect.

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
            ...     .tap_failure_to_iterable(log_err)
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
            ...     .tap_failure_to_iterable(log_err)
            ... )
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('success', (42,))
        """
        return AwaitableResultTupleWrapper.construct_from_awaitable_result(
            self.core
        ).tap_failure_to_iterable(f)

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

    def tap_failure_to_result_iterable(
        self, f: Callable[[_F_default_co], ResultIterable[object, _S]]
    ) -> AwaitableResultTupleWrapper[_F_default_co, _S_default_co | _S]:
        """Apply a synchronous side effect with return type [trcks.ResultIterable][]
        to the wrapped [trcks.Failure][] object.

        Wrapped [trcks.Success][] objects are passed on without side effects.

        Args:
            f: The synchronous side effect to be applied.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - *the original* [trcks.Failure][]
                    if the applied side effect returns a [trcks.Failure][],
                - *the returned* [trcks.SuccessIterable][]
                    if the applied side effect returns a [trcks.SuccessIterable][]
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
            ...     .tap_failure_to_result_iterable(recover)
            ... )
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('success', (0.0, 1.0))
            >>>
            >>> wrapper_2 = (
            ...     AwaitableResultWrapper
            ...     .construct_success(42)
            ...     .tap_failure_to_result_iterable(recover)
            ... )
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('success', (42,))
        """
        return AwaitableResultTupleWrapper.construct_from_awaitable_result(
            self.core
        ).tap_failure_to_result_iterable(f)

    @deprecated("Use tap_failure_to_result_iterable instead")
    def tap_failure_to_result_tuple(
        self, f: Callable[[_F_default_co], ResultTuple[object, _S]]
    ) -> AwaitableResultTupleWrapper[_F_default_co, _S_default_co | _S]:
        """Deprecated alias for
        [trcks.oop.AwaitableResultWrapper.tap_failure_to_result_iterable][].
        """
        return self.tap_failure_to_result_iterable(f)  # pragma: no cover

    @deprecated("Use tap_failure_to_iterable instead")
    def tap_failure_to_tuple(
        self, f: Callable[[_F_default_co], tuple[object, ...]]
    ) -> AwaitableResultTupleWrapper[Never, _F_default_co | _S_default_co]:
        """Deprecated alias for
        [trcks.oop.AwaitableResultWrapper.tap_failure_to_iterable][].
        """
        return self.tap_failure_to_iterable(f)  # pragma: no cover

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

    def tap_success_to_awaitable_result_iterable(
        self, f: Callable[[_S_default_co], AwaitableResultIterable[_F, object]]
    ) -> AwaitableResultTupleWrapper[_F_default_co | _F, _S_default_co]:
        """Apply an asynchronous side effect with return type
        [trcks.AwaitableResultIterable][] to the wrapped [trcks.Success][] object.

        Wrapped [trcks.Failure][] objects are passed on without side effects.

        Args:
            f: The asynchronous side effect to be applied.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - *the original* [trcks.Failure][] if no side effect was applied,
                - *the returned* [trcks.Failure][]
                    if the applied side effect returns a [trcks.Failure][] and
                - *the original* [trcks.Success][] repeated once per element
                    in the returned [trcks.SuccessIterable][]
                    if the applied side effect returns a [trcks.SuccessIterable][].

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
            ...     .tap_success_to_awaitable_result_iterable(write_twice)
            ... )
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('failure', 'missing text')
            >>>
            >>> wrapper_2 = (
            ...     AwaitableResultWrapper
            ...     .construct_success("Hello, world!")
            ...     .tap_success_to_awaitable_result_iterable(write_twice)
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
        ).tap_successes_to_awaitable_result_iterable(f)

    @deprecated("Use tap_success_to_awaitable_result_iterable instead")
    def tap_success_to_awaitable_result_tuple(
        self, f: Callable[[_S_default_co], AwaitableResultTuple[_F, object]]
    ) -> AwaitableResultTupleWrapper[_F_default_co | _F, _S_default_co]:
        """Deprecated alias for
        [trcks.oop.AwaitableResultWrapper.tap_success_to_awaitable_result_iterable][].
        """
        return self.tap_success_to_awaitable_result_iterable(f)  # pragma: no cover

    def tap_success_to_iterable(
        self, f: Callable[[_S_default_co], Iterable[object]]
    ) -> AwaitableResultTupleWrapper[_F_default_co, _S_default_co]:
        """Apply a synchronous side effect returning an [collections.abc.Iterable][]
        to the wrapped [trcks.Success][] object.

        The original success value is repeated once per element
        in the [collections.abc.Iterable][] returned by the side effect.

        Wrapped [trcks.Failure][] objects are passed on without side effects.

        Args:
            f: The synchronous side effect to be applied,
                returning an [collections.abc.Iterable][].

        Returns:
            A [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - *the original* [trcks.Failure][] if no side effect was applied, or
                - an awaitable [trcks.SuccessTuple][] where the original element
                    is repeated once per element in the [collections.abc.Iterable][]
                    returned by the side effect.

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
            ...     .tap_success_to_iterable(log_mult)
            ... )
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('failure', 'error')
            >>>
            >>> wrapper_2 = (
            ...     AwaitableResultWrapper
            ...     .construct_success(7)
            ...     .tap_success_to_iterable(log_mult)
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
        ).tap_successes_to_iterable(f)

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

    def tap_success_to_result_iterable(
        self, f: Callable[[_S_default_co], ResultIterable[_F, object]]
    ) -> AwaitableResultTupleWrapper[_F_default_co | _F, _S_default_co]:
        """Apply a synchronous side effect with return type [trcks.ResultIterable][]
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
                    in the returned [trcks.SuccessIterable][]
                    if the applied side effect returns a [trcks.SuccessIterable][].

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
            ...     .tap_success_to_result_iterable(audit)
            ... )
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('failure', 'missing')
            >>>
            >>> wrapper_2 = (
            ...     AwaitableResultWrapper
            ...     .construct_success("Hello, world!")
            ...     .tap_success_to_result_iterable(audit)
            ... )
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('success', ('Hello, world!', 'Hello, world!'))
        """
        return AwaitableResultTupleWrapper.construct_from_awaitable_result(
            self.core
        ).tap_successes_to_result_iterable(f)

    @deprecated("Use tap_success_to_result_iterable instead")
    def tap_success_to_result_tuple(
        self, f: Callable[[_S_default_co], ResultTuple[_F, object]]
    ) -> AwaitableResultTupleWrapper[_F_default_co | _F, _S_default_co]:
        """Deprecated alias for
        [trcks.oop.AwaitableResultWrapper.tap_success_to_result_iterable][].
        """
        return self.tap_success_to_result_iterable(f)  # pragma: no cover

    @deprecated("Use tap_success_to_iterable instead")
    def tap_success_to_tuple(
        self, f: Callable[[_S_default_co], tuple[object, ...]]
    ) -> AwaitableResultTupleWrapper[_F_default_co, _S_default_co]:
        """Deprecated alias for
        [trcks.oop.AwaitableResultWrapper.tap_success_to_iterable][].
        """
        return self.tap_success_to_iterable(f)  # pragma: no cover
