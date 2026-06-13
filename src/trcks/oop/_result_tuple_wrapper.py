from __future__ import annotations

from typing import TYPE_CHECKING

from trcks import ResultTuple
from trcks._typing import Never, TypeVar, deprecated
from trcks.fp.monads import result_tuple as rt
from trcks.oop._awaitable_result_tuple_wrapper import AwaitableResultTupleWrapper
from trcks.oop._base_wrapper import BaseWrapper

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable, Iterable

    from trcks import (
        AwaitableResult,
        AwaitableResultIterable,
        AwaitableResultTuple,
        Result,
        ResultIterable,
    )

__docformat__ = "google"

_F = TypeVar("_F")
_S = TypeVar("_S")

_F_default = TypeVar("_F_default", default=Never)
_S_default = TypeVar("_S_default", default=Never)

_F_default_co = TypeVar("_F_default_co", covariant=True, default=Never)
_S_default_co = TypeVar("_S_default_co", covariant=True, default=Never)


class ResultTupleWrapper(BaseWrapper[ResultTuple[_F_default_co, _S_default_co]]):
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
        ...     .construct_successes_from_iterable((1, 2, 3))
        ...     .map_successes(double_integer)
        ...     .tap_successes(log_integer)
        ...     .map_successes_to_iterable(duplicate_integer)
        ... )
        Received: 2
        Received: 4
        Received: 6
        >>> result_tuple_wrapper
        ResultTupleWrapper(core=('success', (2, 2, 4, 4, 6, 6)))
    """

    __slots__: tuple[str, ...] = ()

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
    def construct_successes_from_iterable(
        it: Iterable[_S],
    ) -> ResultTupleWrapper[Never, _S]:
        """Construct and wrap a [trcks.SuccessTuple][] object from an iterable.

        Args:
            it: The [collections.abc.Iterable][] to be wrapped and converted.

        Returns:
            A new [trcks.oop.ResultTupleWrapper][] instance with
                the wrapped [trcks.SuccessTuple][] object.

        Example:
            >>> ResultTupleWrapper.construct_successes_from_iterable([1, 2])
            ResultTupleWrapper(core=('success', (1, 2)))
        """
        return ResultTupleWrapper(rt.construct_successes_from_iterable(it))

    @classmethod
    @deprecated(
        "Use construct_successes_from_iterable or the default constructor instead"
    )
    def construct_successes_from_tuple(
        cls,
        tpl: tuple[_S, ...],
    ) -> ResultTupleWrapper[Never, _S]:
        """Deprecated alias for construct_successes_from_iterable."""
        return cls.construct_successes_from_iterable(tpl)  # pragma: no cover

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
            >>> ResultTupleWrapper.construct_successes_from_iterable(
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
            >>> wrapper_2 = ResultTupleWrapper.construct_successes_from_iterable(
            ...     (1, 2)
            ... ).map_failure_to_awaitable(prefix_slowly)
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('success', (1, 2))
        """
        return AwaitableResultTupleWrapper.construct_from_result_iterable(
            self.core
        ).map_failure_to_awaitable(f)

    def map_failure_to_awaitable_result_iterable(
        self, f: Callable[[_F_default_co], AwaitableResultIterable[_F, _S]]
    ) -> AwaitableResultTupleWrapper[_F, _S_default_co | _S]:
        """Apply an asynchronous function with return type
        [trcks.AwaitableResultIterable][] to the wrapped [trcks.Failure][] object.

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
            ... ).map_failure_to_awaitable_result_iterable(recover)
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('success', (0, 1))
            >>>
            >>> wrapper_2 = ResultTupleWrapper.construct_successes_from_iterable(
            ...     (1, 2)
            ... ).map_failure_to_awaitable_result_iterable(recover)
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('success', (1, 2))
        """
        return AwaitableResultTupleWrapper.construct_from_result_iterable(
            self.core
        ).map_failure_to_awaitable_result_iterable(f)

    @deprecated("Use map_failure_to_awaitable_result_iterable instead")
    def map_failure_to_awaitable_result_tuple(
        self, f: Callable[[_F_default_co], AwaitableResultTuple[_F, _S]]
    ) -> AwaitableResultTupleWrapper[_F, _S_default_co | _S]:
        """Deprecated alias for
        [trcks.oop.ResultTupleWrapper.map_failure_to_awaitable_result_iterable][].
        """
        return self.map_failure_to_awaitable_result_iterable(f)  # pragma: no cover

    def map_failure_to_iterable(
        self, f: Callable[[_F_default_co], Iterable[_S]]
    ) -> ResultTupleWrapper[Never, _S_default_co | _S]:
        """Apply a synchronous function returning an [collections.abc.Iterable][]
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
            ... ).map_failure_to_iterable(_recover_from_not_found)
            ResultTupleWrapper(core=('success', (0,)))
            >>>
            >>> ResultTupleWrapper.construct_failure(
            ...     "not authorized"
            ... ).map_failure_to_iterable(_recover_from_not_found)
            ResultTupleWrapper(core=('success', ()))
            >>>
            >>> ResultTupleWrapper.construct_successes_from_iterable(
            ...     (1, 2)
            ... ).map_failure_to_iterable(_recover_from_not_found)
            ResultTupleWrapper(core=('success', (1, 2)))
        """
        mapped_f: Callable[
            [ResultTuple[_F_default_co, _S_default_co]],
            ResultTuple[Never, _S_default_co | _S],
        ] = rt.map_failure_to_iterable(f)
        return ResultTupleWrapper(mapped_f(self.core))

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
            >>> ResultTupleWrapper.construct_successes_from_iterable(
            ...     (1, 2)
            ... ).map_failure_to_result(_recover_from_not_found)
            ResultTupleWrapper(core=('success', (1, 2)))
        """
        mapped_f: Callable[
            [ResultTuple[_F_default_co, _S_default_co]],
            ResultTuple[_F, _S_default_co | _S],
        ] = rt.map_failure_to_result(f)
        return ResultTupleWrapper(mapped_f(self.core))

    def map_failure_to_result_iterable(
        self, f: Callable[[_F_default_co], ResultIterable[_F, _S]]
    ) -> ResultTupleWrapper[_F, _S_default_co | _S]:
        """Apply a synchronous function with return type [trcks.ResultIterable][]
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
            ... ).map_failure_to_result_iterable(_recover_from_not_found)
            ResultTupleWrapper(core=('success', (0,)))
            >>>
            >>> ResultTupleWrapper.construct_failure(
            ...     "not authorized"
            ... ).map_failure_to_result_iterable(_recover_from_not_found)
            ResultTupleWrapper(core=('failure', 'not authorized'))
            >>>
            >>> ResultTupleWrapper.construct_successes_from_iterable(
            ...     (1, 2)
            ... ).map_failure_to_result_iterable(_recover_from_not_found)
            ResultTupleWrapper(core=('success', (1, 2)))
        """
        mapped_f: Callable[
            [ResultTuple[_F_default_co, _S_default_co]],
            ResultTuple[_F, _S_default_co | _S],
        ] = rt.map_failure_to_result_iterable(f)
        return ResultTupleWrapper(mapped_f(self.core))

    @deprecated("Use map_failure_to_result_iterable instead")
    def map_failure_to_result_tuple(
        self, f: Callable[[_F_default_co], ResultTuple[_F, _S]]
    ) -> ResultTupleWrapper[_F, _S_default_co | _S]:
        """Deprecated alias for
        [trcks.oop.ResultTupleWrapper.map_failure_to_result_iterable][].
        """
        return self.map_failure_to_result_iterable(f)  # pragma: no cover

    @deprecated("Use map_failure_to_iterable instead")
    def map_failure_to_tuple(
        self, f: Callable[[_F_default_co], tuple[_S, ...]]
    ) -> ResultTupleWrapper[Never, _S_default_co | _S]:
        """Deprecated alias for
        [trcks.oop.ResultTupleWrapper.map_failure_to_iterable][].
        """
        return self.map_failure_to_iterable(f)  # pragma: no cover

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
            >>> ResultTupleWrapper.construct_successes_from_iterable(
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
            >>> wrapper_2 = ResultTupleWrapper.construct_successes_from_iterable(
            ...     (1, 2)
            ... ).map_successes_to_awaitable(double_slowly)
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('success', (2, 4))
        """
        return AwaitableResultTupleWrapper.construct_from_result_iterable(
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
            >>> wrapper_2 = ResultTupleWrapper.construct_successes_from_iterable(
            ...     (1, 2)
            ... ).map_successes_to_awaitable_result(slowly_double_if_positive)
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('success', (2, 4))
        """
        return AwaitableResultTupleWrapper.construct_from_result_iterable(
            self.core
        ).map_successes_to_awaitable_result(f)

    def map_successes_to_awaitable_result_iterable(
        self, f: Callable[[_S_default_co], AwaitableResultIterable[_F, _S]]
    ) -> AwaitableResultTupleWrapper[_F_default_co | _F, _S]:
        """Apply an asynchronous function with return type
        [trcks.AwaitableResultIterable][] to each element in the wrapped
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
            ... ).map_successes_to_awaitable_result_iterable(slowly_expand)
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('failure', 'not found')
            >>>
            >>> wrapper_2 = ResultTupleWrapper.construct_successes_from_iterable(
            ...     (1, 2)
            ... ).map_successes_to_awaitable_result_iterable(slowly_expand)
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('success', (1, -1, 2, -2))
        """
        return AwaitableResultTupleWrapper.construct_from_result_iterable(
            self.core
        ).map_successes_to_awaitable_result_iterable(f)

    @deprecated("Use map_successes_to_awaitable_result_iterable instead")
    def map_successes_to_awaitable_result_tuple(
        self, f: Callable[[_S_default_co], AwaitableResultTuple[_F, _S]]
    ) -> AwaitableResultTupleWrapper[_F_default_co | _F, _S]:
        """Deprecated alias for
        [trcks.oop.ResultTupleWrapper.map_successes_to_awaitable_result_iterable][].
        """
        return self.map_successes_to_awaitable_result_iterable(f)  # pragma: no cover

    def map_successes_to_iterable(
        self, f: Callable[[_S_default_co], Iterable[_S]]
    ) -> ResultTupleWrapper[_F_default_co, _S]:
        """Apply a synchronous function returning an [collections.abc.Iterable][]
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
            >>> ResultTupleWrapper.construct_successes_from_iterable(
            ...     (1, 2)
            ... ).map_successes_to_iterable(_duplicate_integer)
            ResultTupleWrapper(core=('success', (1, 1, 2, 2)))
            >>>
            >>> ResultTupleWrapper.construct_failure(
            ...     "not found"
            ... ).map_successes_to_iterable(_duplicate_integer)
            ResultTupleWrapper(core=('failure', 'not found'))
        """
        return ResultTupleWrapper(rt.map_successes_to_iterable(f)(self.core))

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
            >>> ResultTupleWrapper.construct_successes_from_iterable(
            ...     (1, 2)
            ... ).map_successes_to_result(double_if_positive)
            ResultTupleWrapper(core=('success', (2, 4)))
            >>>
            >>> ResultTupleWrapper.construct_successes_from_iterable(
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

    def map_successes_to_result_iterable(
        self, f: Callable[[_S_default_co], ResultIterable[_F, _S]]
    ) -> ResultTupleWrapper[_F_default_co | _F, _S]:
        """Apply a synchronous function with return type [trcks.ResultIterable][]
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
            >>> ResultTupleWrapper.construct_successes_from_iterable(
            ...     (1, 2)
            ... ).map_successes_to_result_iterable(duplicate_if_positive)
            ResultTupleWrapper(core=('success', (1, 1, 2, 2)))
            >>>
            >>> ResultTupleWrapper.construct_successes_from_iterable(
            ...     (1, -1, 2)
            ... ).map_successes_to_result_iterable(duplicate_if_positive)
            ResultTupleWrapper(core=('failure', 'not positive'))
            >>>
            >>> ResultTupleWrapper.construct_failure(
            ...     "oops"
            ... ).map_successes_to_result_iterable(duplicate_if_positive)
            ResultTupleWrapper(core=('failure', 'oops'))
        """
        mapped_f: Callable[
            [ResultTuple[_F_default_co, _S_default_co]],
            ResultTuple[_F_default_co | _F, _S],
        ] = rt.map_successes_to_result_iterable(f)
        return ResultTupleWrapper(mapped_f(self.core))

    @deprecated("Use map_successes_to_result_iterable instead")
    def map_successes_to_result_tuple(
        self, f: Callable[[_S_default_co], ResultTuple[_F, _S]]
    ) -> ResultTupleWrapper[_F_default_co | _F, _S]:
        """Deprecated alias for
        [trcks.oop.ResultTupleWrapper.map_successes_to_result_iterable][].
        """
        return self.map_successes_to_result_iterable(f)  # pragma: no cover

    @deprecated("Use map_successes_to_iterable instead")
    def map_successes_to_tuple(
        self, f: Callable[[_S_default_co], tuple[_S, ...]]
    ) -> ResultTupleWrapper[_F_default_co, _S]:
        """Deprecated alias for
        [trcks.oop.ResultTupleWrapper.map_successes_to_iterable][].
        """
        return self.map_successes_to_iterable(f)  # pragma: no cover

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
        return AwaitableResultTupleWrapper.construct_from_result_iterable(
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
        return AwaitableResultTupleWrapper.construct_from_result_iterable(
            self.core
        ).tap_failure_to_awaitable_result(f)

    def tap_failure_to_awaitable_result_iterable(
        self, f: Callable[[_F_default_co], AwaitableResultIterable[object, _S]]
    ) -> AwaitableResultTupleWrapper[_F_default_co, _S_default_co | _S]:
        """Apply an asynchronous side effect with return type
        [trcks.AwaitableResultIterable][] to the wrapped [trcks.Failure][] object.

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
            ... ).tap_failure_to_awaitable_result_iterable(recover)
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('success', (0, 1))
            >>>
            >>> wrapper_2 = ResultTupleWrapper.construct_successes(
            ...     1
            ... ).tap_failure_to_awaitable_result_iterable(recover)
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('success', (1,))
        """
        return AwaitableResultTupleWrapper.construct_from_result_iterable(
            self.core
        ).tap_failure_to_awaitable_result_iterable(f)

    @deprecated("Use tap_failure_to_awaitable_result_iterable instead")
    def tap_failure_to_awaitable_result_tuple(
        self, f: Callable[[_F_default_co], AwaitableResultTuple[object, _S]]
    ) -> AwaitableResultTupleWrapper[_F_default_co, _S_default_co | _S]:
        """Deprecated alias for
        [trcks.oop.ResultTupleWrapper.tap_failure_to_awaitable_result_iterable][].
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

        Wrapped [trcks.SuccessTuple][] objects are passed on without side effects.

        Args:
            f: The synchronous side effect to be applied.

        Returns:
            A new [trcks.oop.ResultTupleWrapper][] instance with

                - a [trcks.SuccessTuple][] containing the original failure
                    repeated once per element
                    in the [collections.abc.Iterable][] returned by the side effect
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
            ... ).tap_failure_to_iterable(_log_and_alert)
            Error logged: critical
            Alert sent: critical
            ResultTupleWrapper(core=('success', ('critical', 'critical')))
            >>>
            >>> ResultTupleWrapper.construct_successes_from_iterable(
            ...     (1, 2)
            ... ).tap_failure_to_iterable(_log_and_alert)
            ResultTupleWrapper(core=('success', (1, 2)))
        """
        tapped_f: Callable[
            [ResultTuple[_F_default_co, _S_default_co]],
            ResultTuple[Never, _F_default_co | _S_default_co],
        ] = rt.tap_failure_to_iterable(f)
        return ResultTupleWrapper(tapped_f(self.core))

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
            >>> ResultTupleWrapper.construct_successes_from_iterable(
            ...     (1, 2)
            ... ).tap_failure_to_result(recover)
            ResultTupleWrapper(core=('success', (1, 2)))
        """
        tapped_f: Callable[
            [ResultTuple[_F_default_co, _S_default_co]],
            ResultTuple[_F_default_co, _S_default_co | _S],
        ] = rt.tap_failure_to_result(f)
        return ResultTupleWrapper(tapped_f(self.core))

    def tap_failure_to_result_iterable(
        self, f: Callable[[_F_default_co], ResultIterable[object, _S]]
    ) -> ResultTupleWrapper[_F_default_co, _S_default_co | _S]:
        """Apply a synchronous side effect with return type [trcks.ResultIterable][]
        to the wrapped [trcks.Failure][] object.

        Wrapped [trcks.SuccessTuple][] objects are passed on without side effects.

        Args:
            f: The synchronous side effect to be applied.

        Returns:
            A new [trcks.oop.ResultTupleWrapper][] instance with

                - *the original* [trcks.Failure][]
                    if the applied side effect returns a [trcks.Failure][],
                - *the returned* [trcks.SuccessIterable][]
                    if the applied side effect returns a [trcks.SuccessIterable][] and
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
            ... ).tap_failure_to_result_iterable(recover)
            ResultTupleWrapper(core=('success', (42,)))
            >>>
            >>> ResultTupleWrapper.construct_failure(
            ...     "fatal"
            ... ).tap_failure_to_result_iterable(recover)
            ResultTupleWrapper(core=('failure', 'fatal'))
            >>>
            >>> ResultTupleWrapper.construct_successes_from_iterable(
            ...     (1, 2)
            ... ).tap_failure_to_result_iterable(recover)
            ResultTupleWrapper(core=('success', (1, 2)))
        """
        tapped_f: Callable[
            [ResultTuple[_F_default_co, _S_default_co]],
            ResultTuple[_F_default_co, _S_default_co | _S],
        ] = rt.tap_failure_to_result_iterable(f)
        return ResultTupleWrapper(tapped_f(self.core))

    @deprecated("Use tap_failure_to_result_iterable instead")
    def tap_failure_to_result_tuple(
        self, f: Callable[[_F_default_co], ResultTuple[object, _S]]
    ) -> ResultTupleWrapper[_F_default_co, _S_default_co | _S]:
        """Deprecated alias for
        [trcks.oop.ResultTupleWrapper.tap_failure_to_result_iterable][].
        """
        return self.tap_failure_to_result_iterable(f)  # pragma: no cover

    @deprecated("Use tap_failure_to_iterable instead")
    def tap_failure_to_tuple(
        self, f: Callable[[_F_default_co], tuple[object, ...]]
    ) -> ResultTupleWrapper[Never, _F_default_co | _S_default_co]:
        """Deprecated alias for
        [trcks.oop.ResultTupleWrapper.tap_failure_to_iterable][].
        """
        return self.tap_failure_to_iterable(f)  # pragma: no cover

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
            ...     ResultTupleWrapper.construct_successes_from_iterable((1, 2))
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
            >>> wrapper_2 = ResultTupleWrapper.construct_successes_from_iterable(
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
        return AwaitableResultTupleWrapper.construct_from_result_iterable(
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
            >>> wrapper_2 = ResultTupleWrapper.construct_successes_from_iterable(
            ...     (1, 2)
            ... ).tap_successes_to_awaitable_result(slowly_check_if_positive)
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('success', (1, 2))
        """
        return AwaitableResultTupleWrapper.construct_from_result_iterable(
            self.core
        ).tap_successes_to_awaitable_result(f)

    def tap_successes_to_awaitable_result_iterable(
        self, f: Callable[[_S_default_co], AwaitableResultIterable[_F, object]]
    ) -> AwaitableResultTupleWrapper[_F_default_co | _F, _S_default_co]:
        """Apply an asynchronous side effect with return type
        [trcks.AwaitableResultIterable][] to each element in the wrapped
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
            ... ).tap_successes_to_awaitable_result_iterable(audit)
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('failure', 'oops')
            >>>
            >>> wrapper_2 = ResultTupleWrapper.construct_successes_from_iterable(
            ...     (1, 2)
            ... ).tap_successes_to_awaitable_result_iterable(audit)
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('success', (1, 1, 2, 2))
        """
        return AwaitableResultTupleWrapper.construct_from_result_iterable(
            self.core
        ).tap_successes_to_awaitable_result_iterable(f)

    @deprecated("Use tap_successes_to_awaitable_result_iterable instead")
    def tap_successes_to_awaitable_result_tuple(
        self, f: Callable[[_S_default_co], AwaitableResultTuple[_F, object]]
    ) -> AwaitableResultTupleWrapper[_F_default_co | _F, _S_default_co]:
        """Deprecated alias for
        [trcks.oop.ResultTupleWrapper.tap_successes_to_awaitable_result_iterable][].
        """
        return self.tap_successes_to_awaitable_result_iterable(f)  # pragma: no cover

    def tap_successes_to_iterable(
        self, f: Callable[[_S_default_co], Iterable[object]]
    ) -> ResultTupleWrapper[_F_default_co, _S_default_co]:
        """Apply a synchronous side effect returning an [collections.abc.Iterable][]
        to each element in the wrapped [trcks.SuccessTuple][].

        The original success elements are repeated once per element
        in the [collections.abc.Iterable][] returned by the side effect.

        Wrapped [trcks.Failure][] objects are passed on without side effects.

        Args:
            f: The synchronous side effect to be applied to each success element.

        Returns:
            A new [trcks.oop.ResultTupleWrapper][] instance with

                - the original [trcks.Failure][] if no side effect was applied, or
                - a [trcks.SuccessTuple][] where each original element is repeated
                    once per element in the [collections.abc.Iterable][]
                    returned by the side effect.

        Example:
            >>> from trcks.oop import ResultTupleWrapper
            >>> def _log_twice(n: int) -> tuple[None, None]:
            ...     return print(f"Received: {n}"), print(f"Received: {n}")
            ...
            >>> ResultTupleWrapper.construct_successes(7).tap_successes_to_iterable(
            ...     _log_twice
            ... )
            Received: 7
            Received: 7
            ResultTupleWrapper(core=('success', (7, 7)))
        """
        return ResultTupleWrapper(rt.tap_successes_to_iterable(f)(self.core))

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
            >>> ResultTupleWrapper.construct_successes_from_iterable(
            ...     (1, 2)
            ... ).tap_successes_to_result(_validate_positive)
            ResultTupleWrapper(core=('success', (1, 2)))
            >>>
            >>> ResultTupleWrapper.construct_successes_from_iterable(
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

    def tap_successes_to_result_iterable(
        self, f: Callable[[_S_default_co], ResultIterable[_F, object]]
    ) -> ResultTupleWrapper[_F_default_co | _F, _S_default_co]:
        """Apply a synchronous side effect with return type [trcks.ResultIterable][]
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
            ... ).tap_successes_to_result_iterable(_validate_positive_twice)
            ResultTupleWrapper(core=('success', (7, 7)))
            >>>
            >>> ResultTupleWrapper.construct_successes_from_iterable(
            ...     (1, -1)
            ... ).tap_successes_to_result_iterable(_validate_positive_twice)
            ResultTupleWrapper(core=('failure', 'not positive'))
        """
        return ResultTupleWrapper(rt.tap_successes_to_result_iterable(f)(self.core))

    @deprecated("Use tap_successes_to_result_iterable instead")
    def tap_successes_to_result_tuple(
        self, f: Callable[[_S_default_co], ResultTuple[_F, object]]
    ) -> ResultTupleWrapper[_F_default_co | _F, _S_default_co]:
        """Deprecated alias for
        [trcks.oop.ResultTupleWrapper.tap_successes_to_result_iterable][].
        """
        return self.tap_successes_to_result_iterable(f)  # pragma: no cover

    @deprecated("Use tap_successes_to_iterable instead")
    def tap_successes_to_tuple(
        self, f: Callable[[_S_default_co], tuple[object, ...]]
    ) -> ResultTupleWrapper[_F_default_co, _S_default_co]:
        """Deprecated alias for
        [trcks.oop.ResultTupleWrapper.tap_successes_to_iterable][].
        """
        return self.tap_successes_to_iterable(f)  # pragma: no cover
