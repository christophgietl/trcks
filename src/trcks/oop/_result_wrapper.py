from __future__ import annotations

from typing import TYPE_CHECKING, final

from trcks import Result
from trcks._typing import Never, TypeVar, deprecated
from trcks.fp.monads import result as r
from trcks.oop._awaitable_result_tuple_wrapper import AwaitableResultTupleWrapper
from trcks.oop._awaitable_result_wrapper import AwaitableResultWrapper
from trcks.oop._base_wrapper import BaseWrapper
from trcks.oop._result_tuple_wrapper import ResultTupleWrapper

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


@final
class ResultWrapper(BaseWrapper[Result[_F_default_co, _S_default_co]]):
    """Type-safe and immutable wrapper for [trcks.Result][] objects.

    The wrapped object can be accessed via the attribute [trcks.oop.BaseWrapper.core][].
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

    __slots__: tuple[str, ...] = ()

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

    def map_failure_to_awaitable_result_iterable(
        self, f: Callable[[_F_default_co], AwaitableResultIterable[_F, _S]]
    ) -> AwaitableResultTupleWrapper[_F, _S_default_co | _S]:
        """Apply an asynchronous function with return type
        [trcks.AwaitableResultIterable][] to the wrapped [trcks.Failure][] object.

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
            ...     .map_failure_to_awaitable_result_iterable(recover)
            ... )
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('success', (0.0, 1.0))
            >>>
            >>> wrapper_2 = (
            ...     ResultWrapper
            ...     .construct_success(25.0)
            ...     .map_failure_to_awaitable_result_iterable(recover)
            ... )
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('success', (25.0,))
        """
        return AwaitableResultTupleWrapper.construct_from_result(
            self.core
        ).map_failure_to_awaitable_result_iterable(f)

    @deprecated("Use map_failure_to_awaitable_result_iterable instead")
    def map_failure_to_awaitable_result_tuple(
        self, f: Callable[[_F_default_co], AwaitableResultTuple[_F, _S]]
    ) -> AwaitableResultTupleWrapper[_F, _S_default_co | _S]:
        """Deprecated alias for
        [trcks.oop.ResultWrapper.map_failure_to_awaitable_result_iterable][].
        """
        return self.map_failure_to_awaitable_result_iterable(f)  # pragma: no cover

    def map_failure_to_iterable(
        self, f: Callable[[_F_default_co], Iterable[_S]]
    ) -> ResultTupleWrapper[Never, _S_default_co | _S]:
        """Apply a synchronous function returning an [collections.abc.Iterable][]
        to the wrapped [trcks.Failure][] object.

        The failure is converted to a [trcks.SuccessTuple][].
        Wrapped [trcks.Success][] objects are passed on unchanged.

        Args:
            f: The synchronous function to be applied,
                returning an [collections.abc.Iterable][].

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
            ... ).map_failure_to_iterable(recover)
            ResultTupleWrapper(core=('success', (0.0, 1.0)))
            >>>
            >>> ResultWrapper.construct_failure(
            ...     "other error"
            ... ).map_failure_to_iterable(recover)
            ResultTupleWrapper(core=('success', ()))
            >>>
            >>> ResultWrapper.construct_success(
            ...     42
            ... ).map_failure_to_iterable(recover)
            ResultTupleWrapper(core=('success', (42,)))
        """
        return ResultTupleWrapper.construct_from_result(
            self.core
        ).map_failure_to_iterable(f)

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

    def map_failure_to_result_iterable(
        self, f: Callable[[_F_default_co], ResultIterable[_F, _S]]
    ) -> ResultTupleWrapper[_F, _S_default_co | _S]:
        """Apply a synchronous function with return type [trcks.ResultIterable][]
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
            ... ).map_failure_to_result_iterable(expand_error)
            ResultTupleWrapper(core=('success', (0.0, 1.0)))
            >>>
            >>> ResultWrapper.construct_failure(
            ...     "other error"
            ... ).map_failure_to_result_iterable(expand_error)
            ResultTupleWrapper(core=('failure', 'other error'))
            >>>
            >>> ResultWrapper.construct_success(
            ...     42
            ... ).map_failure_to_result_iterable(expand_error)
            ResultTupleWrapper(core=('success', (42,)))
        """
        return ResultTupleWrapper.construct_from_result(
            self.core
        ).map_failure_to_result_iterable(f)

    @deprecated("Use map_failure_to_result_iterable instead")
    def map_failure_to_result_tuple(
        self, f: Callable[[_F_default_co], ResultTuple[_F, _S]]
    ) -> ResultTupleWrapper[_F, _S_default_co | _S]:
        """Deprecated alias for
        [trcks.oop.ResultWrapper.map_failure_to_result_iterable][].
        """
        return self.map_failure_to_result_iterable(f)  # pragma: no cover

    @deprecated("Use map_failure_to_iterable instead")
    def map_failure_to_tuple(
        self, f: Callable[[_F_default_co], tuple[_S, ...]]
    ) -> ResultTupleWrapper[Never, _S_default_co | _S]:
        """Deprecated alias for [trcks.oop.ResultWrapper.map_failure_to_iterable][]."""
        return self.map_failure_to_iterable(f)  # pragma: no cover

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

    def map_success_to_awaitable_result_iterable(
        self, f: Callable[[_S_default_co], AwaitableResultIterable[_F, _S]]
    ) -> AwaitableResultTupleWrapper[_F_default_co | _F, _S]:
        """Apply an asynchronous function with return type
        [trcks.AwaitableResultIterable][] to the wrapped [trcks.Success][] object.

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
            ...     .map_success_to_awaitable_result_iterable(slowly_expand)
            ... )
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('failure', 'not found')
            >>>
            >>> wrapper_2 = (
            ...     ResultWrapper
            ...     .construct_success(5.0)
            ...     .map_success_to_awaitable_result_iterable(slowly_expand)
            ... )
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('success', (5.0, 10.0))
        """
        return AwaitableResultTupleWrapper.construct_from_result(
            self.core
        ).map_successes_to_awaitable_result_iterable(f)

    @deprecated("Use map_success_to_awaitable_result_iterable instead")
    def map_success_to_awaitable_result_tuple(
        self, f: Callable[[_S_default_co], AwaitableResultTuple[_F, _S]]
    ) -> AwaitableResultTupleWrapper[_F_default_co | _F, _S]:
        """Deprecated alias for
        [trcks.oop.ResultWrapper.map_success_to_awaitable_result_iterable][].
        """
        return self.map_success_to_awaitable_result_iterable(f)  # pragma: no cover

    def map_success_to_iterable(
        self, f: Callable[[_S_default_co], Iterable[_S]]
    ) -> ResultTupleWrapper[_F_default_co, _S]:
        """Apply a synchronous function returning an [collections.abc.Iterable][]
        to the wrapped [trcks.Success][] object.

        Wrapped [trcks.Failure][] objects are passed on unchanged.

        Args:
            f: The synchronous function to be applied,
                returning an [collections.abc.Iterable][].

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
            ... ).map_success_to_iterable(duplicate)
            ResultTupleWrapper(core=('failure', 'not found'))
            >>>
            >>> ResultWrapper.construct_success(
            ...     5.0
            ... ).map_success_to_iterable(duplicate)
            ResultTupleWrapper(core=('success', (5.0, 5.0)))
        """
        return ResultTupleWrapper.construct_from_result(
            self.core
        ).map_successes_to_iterable(f)

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

    def map_success_to_result_iterable(
        self, f: Callable[[_S_default_co], ResultIterable[_F, _S]]
    ) -> ResultTupleWrapper[_F_default_co | _F, _S]:
        """Apply a synchronous function with return type [trcks.ResultIterable][]
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
            ... ).map_success_to_result_iterable(expand)
            ResultTupleWrapper(core=('failure', 'not found'))
            >>>
            >>> ResultWrapper.construct_success(
            ...     5.0
            ... ).map_success_to_result_iterable(expand)
            ResultTupleWrapper(core=('success', (5.0, 10.0)))
            >>>
            >>> ResultWrapper.construct_success(
            ...     -5.0
            ... ).map_success_to_result_iterable(expand)
            ResultTupleWrapper(core=('failure', 'negative'))
        """
        return ResultTupleWrapper.construct_from_result(
            self.core
        ).map_successes_to_result_iterable(f)

    @deprecated("Use map_success_to_result_iterable instead")
    def map_success_to_result_tuple(
        self, f: Callable[[_S_default_co], ResultTuple[_F, _S]]
    ) -> ResultTupleWrapper[_F_default_co | _F, _S]:
        """Deprecated alias for
        [trcks.oop.ResultWrapper.map_success_to_result_iterable][].
        """
        return self.map_success_to_result_iterable(f)  # pragma: no cover

    @deprecated("Use map_success_to_iterable instead")
    def map_success_to_tuple(
        self, f: Callable[[_S_default_co], tuple[_S, ...]]
    ) -> ResultTupleWrapper[_F_default_co, _S]:
        """Deprecated alias for [trcks.oop.ResultWrapper.map_success_to_iterable][]."""
        return self.map_success_to_iterable(f)  # pragma: no cover

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

    def tap_failure_to_awaitable_result_iterable(
        self, f: Callable[[_F_default_co], AwaitableResultIterable[object, _S]]
    ) -> AwaitableResultTupleWrapper[_F_default_co, _S_default_co | _S]:
        """Apply an asynchronous side effect with return type
        [trcks.AwaitableResultIterable][] to the wrapped [trcks.Failure][] object.

        Wrapped [trcks.Success][] objects are passed on without side effects.

        Args:
            f: The asynchronous side effect to be applied.

        Returns:
            A [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - *the original* [trcks.Failure][]
                    if the applied side effect returns a [trcks.Failure][],
                - *the returned* [trcks.SuccessIterable][]
                    if the applied side effect returns a [trcks.SuccessIterable][]
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
            ...     .tap_failure_to_awaitable_result_iterable(recover)
            ... )
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('success', (0.0, 1.0))
            >>>
            >>> wrapper_2 = (
            ...     ResultWrapper
            ...     .construct_success(42)
            ...     .tap_failure_to_awaitable_result_iterable(recover)
            ... )
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('success', (42,))
        """
        return AwaitableResultTupleWrapper.construct_from_result(
            self.core
        ).tap_failure_to_awaitable_result_iterable(f)

    @deprecated("Use tap_failure_to_awaitable_result_iterable instead")
    def tap_failure_to_awaitable_result_tuple(
        self, f: Callable[[_F_default_co], AwaitableResultTuple[object, _S]]
    ) -> AwaitableResultTupleWrapper[_F_default_co, _S_default_co | _S]:
        """Deprecated alias for
        [trcks.oop.ResultWrapper.tap_failure_to_awaitable_result_iterable][].
        """
        return self.tap_failure_to_awaitable_result_iterable(f)  # pragma: no cover

    def tap_failure_to_iterable(
        self, f: Callable[[_F_default_co], Iterable[object]]
    ) -> ResultTupleWrapper[Never, _F_default_co | _S_default_co]:
        """Apply a synchronous side effect returning an [collections.abc.Iterable][]
        to the wrapped [trcks.Failure][] object.

        The failure is converted to a [trcks.SuccessTuple][] where
        the original failure value is repeated once per element in
        the [collections.abc.Iterable][] returned by the side effect.

        Wrapped [trcks.Success][] objects are passed on without side effects.

        Args:
            f: The synchronous side effect to be applied,
                returning an [collections.abc.Iterable][].

        Returns:
            A [trcks.oop.ResultTupleWrapper][] instance with

                - a [trcks.SuccessTuple][] containing the original failure
                    repeated once per element
                    in the [collections.abc.Iterable][] returned by the side effect
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
            ... ).tap_failure_to_iterable(log_err)
            Error logged: critical
            Alert sent: critical
            ResultTupleWrapper(core=('success', ('critical', 'critical')))
            >>>
            >>> ResultWrapper.construct_success(
            ...     42
            ... ).tap_failure_to_iterable(log_err)
            ResultTupleWrapper(core=('success', (42,)))
        """
        return ResultTupleWrapper.construct_from_result(
            self.core
        ).tap_failure_to_iterable(f)

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

    def tap_failure_to_result_iterable(
        self, f: Callable[[_F_default_co], ResultIterable[object, _S]]
    ) -> ResultTupleWrapper[_F_default_co, _S_default_co | _S]:
        """Apply a synchronous side effect with return type [trcks.ResultIterable][]
        to the wrapped [trcks.Failure][] object.

        Wrapped [trcks.Success][] objects are passed on without side effects.

        Args:
            f: The synchronous side effect to be applied.

        Returns:
            A [trcks.oop.ResultTupleWrapper][] instance with

                - *the original* [trcks.Failure][]
                    if the applied side effect returns a [trcks.Failure][],
                - *the returned* [trcks.SuccessIterable][]
                    if the applied side effect returns a [trcks.SuccessIterable][] and
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
            ... ).tap_failure_to_result_iterable(attempt_recover)
            ResultTupleWrapper(core=('success', (99,)))
            >>>
            >>> ResultWrapper.construct_failure(
            ...     "fatal"
            ... ).tap_failure_to_result_iterable(attempt_recover)
            ResultTupleWrapper(core=('failure', 'fatal'))
            >>>
            >>> ResultWrapper.construct_success(
            ...     42
            ... ).tap_failure_to_result_iterable(attempt_recover)
            ResultTupleWrapper(core=('success', (42,)))
        """
        return ResultTupleWrapper.construct_from_result(
            self.core
        ).tap_failure_to_result_iterable(f)

    @deprecated("Use tap_failure_to_result_iterable instead")
    def tap_failure_to_result_tuple(
        self, f: Callable[[_F_default_co], ResultTuple[object, _S]]
    ) -> ResultTupleWrapper[_F_default_co, _S_default_co | _S]:
        """Deprecated alias for
        [trcks.oop.ResultWrapper.tap_failure_to_result_iterable][].
        """
        return self.tap_failure_to_result_iterable(f)  # pragma: no cover

    @deprecated("Use tap_failure_to_iterable instead")
    def tap_failure_to_tuple(
        self, f: Callable[[_F_default_co], tuple[object, ...]]
    ) -> ResultTupleWrapper[Never, _F_default_co | _S_default_co]:
        """Deprecated alias for [trcks.oop.ResultWrapper.tap_failure_to_iterable][]."""
        return self.tap_failure_to_iterable(f)  # pragma: no cover

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

    def tap_success_to_awaitable_result_iterable(
        self, f: Callable[[_S_default_co], AwaitableResultIterable[_F, object]]
    ) -> AwaitableResultTupleWrapper[_F_default_co | _F, _S_default_co]:
        """Apply an asynchronous side effect with return type
        [trcks.AwaitableResultIterable][] to the wrapped [trcks.Success][] object.

        Wrapped [trcks.Failure][] objects are passed on without side effects.

        Args:
            f: The asynchronous side effect to be applied.

        Returns:
            A [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - *the original* [trcks.Failure][] if no side effect was applied,
                - *the returned* [trcks.Failure][]
                    if the applied side effect returns a [trcks.Failure][] and
                - *the original* [trcks.Success][] repeated once per element
                    in the returned [trcks.SuccessIterable][]
                    if the applied side effect returns a [trcks.SuccessIterable][].

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
            ...     .tap_success_to_awaitable_result_iterable(write_twice)
            ... )
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('failure', 'missing text')
            >>>
            >>> wrapper_2 = (
            ...     ResultWrapper
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
        return AwaitableResultTupleWrapper.construct_from_result(
            self.core
        ).tap_successes_to_awaitable_result_iterable(f)

    @deprecated("Use tap_success_to_awaitable_result_iterable instead")
    def tap_success_to_awaitable_result_tuple(
        self, f: Callable[[_S_default_co], AwaitableResultTuple[_F, object]]
    ) -> AwaitableResultTupleWrapper[_F_default_co | _F, _S_default_co]:
        """Deprecated alias for
        [trcks.oop.ResultWrapper.tap_success_to_awaitable_result_iterable][].
        """
        return self.tap_success_to_awaitable_result_iterable(f)  # pragma: no cover

    def tap_success_to_iterable(
        self, f: Callable[[_S_default_co], Iterable[object]]
    ) -> ResultTupleWrapper[_F_default_co, _S_default_co]:
        """Apply a synchronous side effect returning an [collections.abc.Iterable][]
        to the wrapped [trcks.Success][] object.

        The original success value is repeated once per element
        in the [collections.abc.Iterable][] returned by the side effect.

        Wrapped [trcks.Failure][] objects are passed on without side effects.

        Args:
            f: The synchronous side effect to be applied,
                returning an [collections.abc.Iterable][].

        Returns:
            A [trcks.oop.ResultTupleWrapper][] instance with

                - *the original* [trcks.Failure][] if no side effect was applied, or
                - a [trcks.SuccessTuple][] where the original element is repeated
                    once per element in the [collections.abc.Iterable][]
                    returned by the side effect.

        Example:
            >>> from trcks.oop import ResultWrapper
            >>> def log_mult(n: int) -> tuple[None, ...]:
            ...     print(f"v={n}")
            ...     print(f"v={n}")
            ...     return None, None
            ...
            >>> ResultWrapper.construct_failure(
            ...     "error"
            ... ).tap_success_to_iterable(log_mult)
            ResultTupleWrapper(core=('failure', 'error'))
            >>>
            >>> ResultWrapper.construct_success(
            ...     7
            ... ).tap_success_to_iterable(log_mult)
            v=7
            v=7
            ResultTupleWrapper(core=('success', (7, 7)))
        """
        return ResultTupleWrapper.construct_from_result(
            self.core
        ).tap_successes_to_iterable(f)

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

    def tap_success_to_result_iterable(
        self, f: Callable[[_S_default_co], ResultIterable[_F, object]]
    ) -> ResultTupleWrapper[_F_default_co | _F, _S_default_co]:
        """Apply a synchronous side effect with return type [trcks.ResultIterable][]
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
                    returns [trcks.SuccessIterable][].

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
            ... ).tap_success_to_result_iterable(audit)
            ResultTupleWrapper(core=('failure', 'oops'))
            >>>
            >>> ResultWrapper.construct_success(
            ...     7
            ... ).tap_success_to_result_iterable(audit)
            ResultTupleWrapper(core=('success', (7, 7)))
            >>>
            >>> ResultWrapper.construct_success(
            ...     -1
            ... ).tap_success_to_result_iterable(audit)
            ResultTupleWrapper(core=('failure', 'negative'))
        """
        return ResultTupleWrapper.construct_from_result(
            self.core
        ).tap_successes_to_result_iterable(f)

    @deprecated("Use tap_success_to_result_iterable instead")
    def tap_success_to_result_tuple(
        self, f: Callable[[_S_default_co], ResultTuple[_F, object]]
    ) -> ResultTupleWrapper[_F_default_co | _F, _S_default_co]:
        """Deprecated alias for
        [trcks.oop.ResultWrapper.tap_success_to_result_iterable][].
        """
        return self.tap_success_to_result_iterable(f)  # pragma: no cover

    @deprecated("Use tap_success_to_iterable instead")
    def tap_success_to_tuple(
        self, f: Callable[[_S_default_co], tuple[object, ...]]
    ) -> ResultTupleWrapper[_F_default_co, _S_default_co]:
        """Deprecated alias for [trcks.oop.ResultWrapper.tap_success_to_iterable][]."""
        return self.tap_success_to_iterable(f)  # pragma: no cover
