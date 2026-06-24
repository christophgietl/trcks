from __future__ import annotations

from typing import TYPE_CHECKING, final

from trcks._typing import TypeVar, deprecated
from trcks.fp.monads import tuple_ as t
from trcks.oop._awaitable_result_tuple_wrapper import AwaitableResultTupleWrapper
from trcks.oop._awaitable_tuple_wrapper import AwaitableTupleWrapper
from trcks.oop._base_wrapper import BaseWrapper
from trcks.oop._result_tuple_wrapper import ResultTupleWrapper

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable, Iterable

    from trcks import (
        AwaitableIterable,
        AwaitableResult,
        AwaitableResultIterable,
        AwaitableResultTuple,
        AwaitableTuple,
        Result,
        ResultIterable,
        ResultTuple,
    )

__docformat__ = "google"

_F = TypeVar("_F")
_S = TypeVar("_S")
_T = TypeVar("_T")

_T_co = TypeVar("_T_co", covariant=True)


@final
class TupleWrapper(BaseWrapper[tuple[_T_co, ...]]):
    """Type-safe and immutable wrapper for homogeneous [tuple][] objects.

    The wrapped homogeneous [tuple][] can be accessed
    via the attribute [trcks.oop.BaseWrapper.core][].
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
        ...     .construct_from_iterable((1, 2, 3))
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
        ...     .construct_from_iterable((1, 2, 3))
        ...     .map_to_iterable(duplicate_integer)
        ... )
        >>> tuple_wrapper
        TupleWrapper(core=(1, 1, 2, 2, 3, 3))
    """

    __slots__: tuple[str, ...] = ()

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
    def construct_from_iterable(it: Iterable[_T]) -> TupleWrapper[_T]:
        """Wrap a [collections.abc.Iterable][] object and convert it into a [tuple][].

        Args:
            it: The [collections.abc.Iterable][] to be wrapped and converted.

        Returns:
            A new [trcks.oop.TupleWrapper][] instance with
                the wrapped [collections.abc.Iterable][] converted into a [tuple][].

        Example:
            >>> from trcks.oop import TupleWrapper
            >>> tuple_wrapper: TupleWrapper[int] = TupleWrapper.construct_from_iterable(
            ...     [1, 2, 3]
            ... )
            >>> tuple_wrapper
            TupleWrapper(core=(1, 2, 3))
        """
        return TupleWrapper(tuple(it))

    @classmethod
    @deprecated("Use construct_from_iterable or the default constructor instead")
    def construct_from_tuple(cls, tpl: tuple[_T, ...]) -> TupleWrapper[_T]:
        """Deprecated alias for construct_from_iterable."""
        return cls.construct_from_iterable(tpl)  # pragma: no cover

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
            ...     .construct_from_iterable((1, 2, 3))
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
            ...     .construct_from_iterable((1, 2, 3))
            ...     .map_to_awaitable(slowly_add_one)
            ... )
            >>> awaitable_tuple_wrapper
            AwaitableTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_tuple_wrapper.core_as_coroutine)
            (2, 3, 4)
        """
        return AwaitableTupleWrapper.construct_from_iterable(
            self.core
        ).map_to_awaitable(f)

    def map_to_awaitable_iterable(
        self, f: Callable[[_T_co], AwaitableIterable[_T]]
    ) -> AwaitableTupleWrapper[_T]:
        """Apply an asynchronous function returning a [trcks.AwaitableIterable][]
        to each element in the wrapped homogeneous [tuple][] and flatten.

        Args:
            f: The asynchronous function to be applied to each element,
                returning a [trcks.AwaitableIterable][].

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
            ...     .construct_from_iterable((1, 2))
            ...     .map_to_awaitable_iterable(slowly_duplicate)
            ... )
            >>> awaitable_tuple_wrapper
            AwaitableTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_tuple_wrapper.core_as_coroutine)
            (1, 1, 2, 2)
        """
        return AwaitableTupleWrapper.construct_from_iterable(
            self.core
        ).map_to_awaitable_iterable(f)

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
            ...     .construct_from_iterable((1, 2))
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
            ...     .construct_from_iterable((1, -1, 2))
            ...     .map_to_awaitable_result(slowly_double_if_positive)
            ... )
            >>> awaitable_result_tuple_wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_result_tuple_wrapper_2.core_as_coroutine)
            ('failure', 'negative')
        """
        return AwaitableResultTupleWrapper.construct_successes_from_iterable(
            self.core
        ).map_successes_to_awaitable_result(f)

    def map_to_awaitable_result_iterable(
        self, f: Callable[[_T_co], AwaitableResultIterable[_F, _S]]
    ) -> AwaitableResultTupleWrapper[_F, _S]:
        """Apply an asynchronous function with return type
        [trcks.AwaitableResultIterable][] to each element in the wrapped
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
            ...     .construct_from_iterable((1, 2))
            ...     .map_to_awaitable_result_iterable(slowly_expand_if_positive)
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
            ...     .construct_from_iterable((1, -1, 2))
            ...     .map_to_awaitable_result_iterable(slowly_expand_if_positive)
            ... )
            >>> awaitable_result_tuple_wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_result_tuple_wrapper_2.core_as_coroutine)
            ('failure', 'negative')
        """
        return AwaitableResultTupleWrapper.construct_successes_from_iterable(
            self.core
        ).map_successes_to_awaitable_result_iterable(f)

    @deprecated("Use map_to_awaitable_result_iterable instead")
    def map_to_awaitable_result_tuple(
        self, f: Callable[[_T_co], AwaitableResultTuple[_F, _S]]
    ) -> AwaitableResultTupleWrapper[_F, _S]:
        """Deprecated alias for
        [trcks.oop.TupleWrapper.map_to_awaitable_result_iterable][].
        """
        return self.map_to_awaitable_result_iterable(f)  # pragma: no cover

    @deprecated("Use map_to_awaitable_iterable instead")
    def map_to_awaitable_tuple(
        self, f: Callable[[_T_co], AwaitableTuple[_T]]
    ) -> AwaitableTupleWrapper[_T]:
        """Deprecated alias for [trcks.oop.TupleWrapper.map_to_awaitable_iterable][]."""
        return self.map_to_awaitable_iterable(f)  # pragma: no cover

    def map_to_iterable(self, f: Callable[[_T_co], Iterable[_T]]) -> TupleWrapper[_T]:
        """Apply a function returning an [collections.abc.Iterable][] to each element
        in the wrapped homogeneous [tuple][] and flatten the result.

        Args:
            f: The function to be applied to each element,
                returning an [collections.abc.Iterable][].

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
            ...     .construct_from_iterable((1, 2, 3))
            ...     .map_to_iterable(duplicate_integer)
            ... )
            >>> tuple_wrapper
            TupleWrapper(core=(1, 1, 2, 2, 3, 3))
        """
        return TupleWrapper(t.map_to_iterable(f)(self.core))

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
            >>> TupleWrapper.construct_from_iterable(
            ...     (1, 2, 3)
            ... ).map_to_result(double_if_positive)
            ResultTupleWrapper(core=('success', (2, 4, 6)))
            >>>
            >>> TupleWrapper.construct_from_iterable(
            ...     (1, -1, 2)
            ... ).map_to_result(double_if_positive)
            ResultTupleWrapper(core=('failure', 'negative'))
        """
        return ResultTupleWrapper.construct_successes_from_iterable(
            self.core
        ).map_successes_to_result(f)

    def map_to_result_iterable(
        self, f: Callable[[_T_co], ResultIterable[_F, _S]]
    ) -> ResultTupleWrapper[_F, _S]:
        """Apply a synchronous function with return type [trcks.ResultIterable][]
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
            >>> TupleWrapper.construct_from_iterable(
            ...     (1, 2)
            ... ).map_to_result_iterable(expand_if_positive)
            ResultTupleWrapper(core=('success', (1, -1, 2, -2)))
            >>>
            >>> TupleWrapper.construct_from_iterable(
            ...     (1, -1, 2)
            ... ).map_to_result_iterable(expand_if_positive)
            ResultTupleWrapper(core=('failure', 'negative'))
        """
        return ResultTupleWrapper.construct_successes_from_iterable(
            self.core
        ).map_successes_to_result_iterable(f)

    @deprecated("Use map_to_result_iterable instead")
    def map_to_result_tuple(
        self, f: Callable[[_T_co], ResultTuple[_F, _S]]
    ) -> ResultTupleWrapper[_F, _S]:
        """Deprecated alias for [trcks.oop.TupleWrapper.map_to_result_iterable][]."""
        return self.map_to_result_iterable(f)  # pragma: no cover

    @deprecated("Use map_to_iterable instead")
    def map_to_tuple(self, f: Callable[[_T_co], tuple[_T, ...]]) -> TupleWrapper[_T]:
        """Deprecated alias for [trcks.oop.TupleWrapper.map_to_iterable][]."""
        return self.map_to_iterable(f)  # pragma: no cover

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
            ...     .construct_from_iterable((1, 2, 3))
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
            ...     .construct_from_iterable((1, 2, 3))
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
        return AwaitableTupleWrapper.construct_from_iterable(
            self.core
        ).tap_to_awaitable(f)

    def tap_to_awaitable_iterable(
        self, f: Callable[[_T_co], AwaitableIterable[object]]
    ) -> AwaitableTupleWrapper[_T_co]:
        """Apply an asynchronous side effect returning a [trcks.AwaitableIterable][]
        to each element in the wrapped homogeneous [tuple][].

        Args:
            f: The asynchronous side effect to be applied to each element,
                returning a [trcks.AwaitableIterable][].

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
            ...     .construct_from_iterable((1, 2, 3))
            ...     .tap_to_awaitable_iterable(write_to_disk)
            ... )
            >>> awaitable_tuple_wrapper
            AwaitableTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_tuple_wrapper.core_as_coroutine)
            Wrote 1 to disk.
            Wrote 2 to disk.
            Wrote 3 to disk.
            (1, 1, 2, 2, 3, 3)
        """
        return AwaitableTupleWrapper.construct_from_iterable(
            self.core
        ).tap_to_awaitable_iterable(f)

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
            ...     .construct_from_iterable((1, 2))
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
            ...     .construct_from_iterable((1, -1, 2))
            ...     .tap_to_awaitable_result(slowly_check_if_positive)
            ... )
            >>> awaitable_result_tuple_wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_result_tuple_wrapper_2.core_as_coroutine)
            ('failure', 'negative')
        """
        return AwaitableResultTupleWrapper.construct_successes_from_iterable(
            self.core
        ).tap_successes_to_awaitable_result(f)

    def tap_to_awaitable_result_iterable(
        self, f: Callable[[_T_co], AwaitableResultIterable[_F, object]]
    ) -> AwaitableResultTupleWrapper[_F, _T_co]:
        """Apply an asynchronous side effect with return type
        [trcks.AwaitableResultIterable][] to each element in the wrapped
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
            ...     .construct_from_iterable((1, 2))
            ...     .tap_to_awaitable_result_iterable(audit)
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
            ...     .construct_from_iterable((1, -1, 2))
            ...     .tap_to_awaitable_result_iterable(audit)
            ... )
            >>> awaitable_result_tuple_wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_result_tuple_wrapper_2.core_as_coroutine)
            ('failure', 'negative')
        """
        return AwaitableResultTupleWrapper.construct_successes_from_iterable(
            self.core
        ).tap_successes_to_awaitable_result_iterable(f)

    @deprecated("Use tap_to_awaitable_result_iterable instead")
    def tap_to_awaitable_result_tuple(
        self, f: Callable[[_T_co], AwaitableResultTuple[_F, object]]
    ) -> AwaitableResultTupleWrapper[_F, _T_co]:
        """Deprecated alias for
        [trcks.oop.TupleWrapper.tap_to_awaitable_result_iterable][].
        """
        return self.tap_to_awaitable_result_iterable(f)  # pragma: no cover

    @deprecated("Use tap_to_awaitable_iterable instead")
    def tap_to_awaitable_tuple(
        self, f: Callable[[_T_co], AwaitableTuple[object]]
    ) -> AwaitableTupleWrapper[_T_co]:
        """Deprecated alias for [trcks.oop.TupleWrapper.tap_to_awaitable_iterable][]."""
        return self.tap_to_awaitable_iterable(f)  # pragma: no cover

    def tap_to_iterable(
        self, f: Callable[[_T_co], Iterable[object]]
    ) -> TupleWrapper[_T_co]:
        """Apply a side effect returning an [collections.abc.Iterable][] to each element
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
            ...     .construct_from_iterable((1, 2, 3, 4))
            ...     .tap_to_iterable(get_divisors)
            ... )
            >>> tuple_wrapper
            TupleWrapper(core=(1, 2, 2, 3, 3, 4, 4, 4))
        """
        return TupleWrapper(t.tap_to_iterable(f)(self.core))

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
            >>> TupleWrapper.construct_from_iterable(
            ...     (1, 2)
            ... ).tap_to_result(audit)
            ResultTupleWrapper(core=('success', (1, 2)))
            >>>
            >>> TupleWrapper.construct_from_iterable(
            ...     (1, -1, 2)
            ... ).tap_to_result(audit)
            ResultTupleWrapper(core=('failure', 'negative'))
        """
        return ResultTupleWrapper.construct_successes_from_iterable(
            self.core
        ).tap_successes_to_result(f)

    def tap_to_result_iterable(
        self, f: Callable[[_T_co], ResultIterable[_F, object]]
    ) -> ResultTupleWrapper[_F, _T_co]:
        """Apply a synchronous side effect with return type [trcks.ResultIterable][]
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
            >>> TupleWrapper.construct_from_iterable(
            ...     (7,)
            ... ).tap_to_result_iterable(audit)
            ResultTupleWrapper(core=('success', (7, 7)))
            >>>
            >>> TupleWrapper.construct_from_iterable(
            ...     (1, -1)
            ... ).tap_to_result_iterable(audit)
            ResultTupleWrapper(core=('failure', 'negative'))
        """
        return ResultTupleWrapper.construct_successes_from_iterable(
            self.core
        ).tap_successes_to_result_iterable(f)

    @deprecated("Use tap_to_result_iterable instead")
    def tap_to_result_tuple(
        self, f: Callable[[_T_co], ResultTuple[_F, object]]
    ) -> ResultTupleWrapper[_F, _T_co]:
        """Deprecated alias for [trcks.oop.TupleWrapper.tap_to_result_iterable][]."""
        return self.tap_to_result_iterable(f)  # pragma: no cover

    @deprecated("Use tap_to_iterable instead")
    def tap_to_tuple(
        self, f: Callable[[_T_co], tuple[object, ...]]
    ) -> TupleWrapper[_T_co]:
        """Deprecated alias for [trcks.oop.TupleWrapper.tap_to_iterable][]."""
        return self.tap_to_iterable(f)  # pragma: no cover
