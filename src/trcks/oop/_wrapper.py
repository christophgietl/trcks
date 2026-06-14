from __future__ import annotations

from typing import TYPE_CHECKING

from trcks._typing import TypeVar, deprecated
from trcks.fp.monads import awaitable as a
from trcks.fp.monads import awaitable_result as ar
from trcks.fp.monads import identity as i
from trcks.fp.monads import result as r
from trcks.oop._awaitable_result_tuple_wrapper import AwaitableResultTupleWrapper
from trcks.oop._awaitable_result_wrapper import AwaitableResultWrapper
from trcks.oop._awaitable_tuple_wrapper import AwaitableTupleWrapper
from trcks.oop._awaitable_wrapper import AwaitableWrapper
from trcks.oop._base_wrapper import BaseWrapper
from trcks.oop._result_tuple_wrapper import ResultTupleWrapper
from trcks.oop._result_wrapper import ResultWrapper
from trcks.oop._tuple_wrapper import TupleWrapper

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


class Wrapper(BaseWrapper[_T_co]):
    """Type-safe and immutable wrapper for arbitrary objects.

    The wrapped object can be accessed via the attribute [trcks.oop.BaseWrapper.core][].
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

    __slots__: tuple[str, ...] = ()

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

    def map_to_awaitable_iterable(
        self, f: Callable[[_T_co], AwaitableIterable[_T]]
    ) -> AwaitableTupleWrapper[_T]:
        """Apply an asynchronous function returning a [collections.abc.Iterable][]
        to the wrapped object.

        Args:
            f: The asynchronous function to be applied, returning a
                [collections.abc.Iterable][].

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
            ...         Wrapper.construct(7).map_to_awaitable_iterable(slowly_duplicate)
            ...     )
            ...     result_tuple = await awaitable_tuple_wrapper.core
            ...     assert len(result_tuple) == 2
            ...     return result_tuple
            ...
            >>> asyncio.run(main())
            (7, 7)
        """
        return AwaitableTupleWrapper(a.map_(tuple)(f(self.core)))

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

    def map_to_awaitable_result_iterable(
        self, f: Callable[[_T_co], AwaitableResultIterable[_F, _S]]
    ) -> AwaitableResultTupleWrapper[_F, _S]:
        """Apply an asynchronous function with return type
        [trcks.AwaitableResultIterable][] to the wrapped object.

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
            ...     .map_to_awaitable_result_iterable(validate)
            ... )
            >>> wrapper
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper.core_as_coroutine)
            ('success', (5.0, 10.0))
        """
        return AwaitableResultTupleWrapper(ar.map_success(tuple)(f(self.core)))

    @deprecated("Use map_to_awaitable_result_iterable instead")
    def map_to_awaitable_result_tuple(
        self, f: Callable[[_T_co], AwaitableResultTuple[_F, _S]]
    ) -> AwaitableResultTupleWrapper[_F, _S]:
        """Deprecated alias for
        [trcks.oop.Wrapper.map_to_awaitable_result_iterable][].
        """
        return self.map_to_awaitable_result_iterable(f)  # pragma: no cover

    @deprecated("Use map_to_awaitable_iterable instead")
    def map_to_awaitable_tuple(
        self, f: Callable[[_T_co], AwaitableTuple[_T]]
    ) -> AwaitableTupleWrapper[_T]:
        """Deprecated alias for [trcks.oop.Wrapper.map_to_awaitable_iterable][]."""
        return self.map_to_awaitable_iterable(f)  # pragma: no cover

    def map_to_iterable(self, f: Callable[[_T_co], Iterable[_T]]) -> TupleWrapper[_T]:
        """Apply a function returning an [collections.abc.Iterable][]
        to the wrapped object.

        Args:
            f: The function to be applied, returning a [collections.abc.Iterable][].

        Returns:
            A [trcks.oop.TupleWrapper][] instance with
                the result of the function application.

        Example:
            >>> from trcks.oop import Wrapper
            >>> def duplicate(n: int) -> tuple[int, int]:
            ...     return n, n
            ...
            >>> Wrapper.construct(3).map_to_iterable(duplicate)
            TupleWrapper(core=(3, 3))
        """
        return TupleWrapper(tuple(f(self.core)))

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

    def map_to_result_iterable(
        self, f: Callable[[_T_co], ResultIterable[_F, _S]]
    ) -> ResultTupleWrapper[_F, _S]:
        """Apply a synchronous function with return type [trcks.ResultIterable][]
        to the wrapped object.

        Args:
            f: The synchronous function to be applied.

        Returns:
            A [trcks.oop.ResultTupleWrapper][] instance with
                the result of the function application.

        Example:
            >>> from trcks import ResultTuple
            >>> Wrapper.construct(-1).map_to_result_iterable(
            ...     lambda n: ("success", (n, n))
            ...     if n >= 0
            ...     else ("failure", "negative value")
            ... )
            ResultTupleWrapper(core=('failure', 'negative value'))
        """
        return ResultTupleWrapper(r.map_success(tuple)(f(self.core)))

    @deprecated("Use map_to_result_iterable instead")
    def map_to_result_tuple(
        self, f: Callable[[_T_co], ResultTuple[_F, _S]]
    ) -> ResultTupleWrapper[_F, _S]:
        """Deprecated alias for [trcks.oop.Wrapper.map_to_result_iterable][]."""
        return self.map_to_result_iterable(f)  # pragma: no cover

    @deprecated("Use map_to_iterable instead")
    def map_to_tuple(self, f: Callable[[_T_co], tuple[_T, ...]]) -> TupleWrapper[_T]:
        """Deprecated alias for [trcks.oop.Wrapper.map_to_iterable][]."""
        return self.map_to_iterable(f)  # pragma: no cover

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

    def tap_to_awaitable_iterable(
        self, f: Callable[[_T_co], AwaitableIterable[object]]
    ) -> AwaitableTupleWrapper[_T_co]:
        """Apply an asynchronous side effect returning a [trcks.AwaitableIterable][]
        to the wrapped object.

        Args:
            f: The asynchronous side effect to be applied,
                returning a [trcks.AwaitableIterable][].

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
            ... ).tap_to_awaitable_iterable(write_to_disk)
            >>> asyncio.run(awaitable_tuple_wrapper.core_as_coroutine)
            Wrote 3 to disk.
            (3, 3)
        """
        return AwaitableTupleWrapper.construct(self.core).tap_to_awaitable_iterable(f)

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

    def tap_to_awaitable_result_iterable(
        self, f: Callable[[_T_co], AwaitableResultIterable[_F, object]]
    ) -> AwaitableResultTupleWrapper[_F, _T_co]:
        """Apply an asynchronous side effect with return type
        [trcks.AwaitableResultIterable][] to the wrapped object.

        Args:
            f: The asynchronous side effect to be applied.

        Returns:
            A [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - *the returned* [trcks.Failure][]
                    if the given side effect returns a [trcks.Failure][] or
                - *the original* wrapped object repeated once per element
                    in the side effect output if the given side effect
                    returns [trcks.SuccessIterable][].

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
            ... ).tap_to_awaitable_result_iterable(write_twice)
            >>> wrapper
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> result = asyncio.run(wrapper.core_as_coroutine)
            Wrote 'Hello, world!' twice.
            >>> result
            ('success', ('Hello, world!', 'Hello, world!'))
        """
        return AwaitableResultTupleWrapper.construct_successes(
            self.core
        ).tap_successes_to_awaitable_result_iterable(f)

    @deprecated("Use tap_to_awaitable_result_iterable instead")
    def tap_to_awaitable_result_tuple(
        self, f: Callable[[_T_co], AwaitableResultTuple[_F, object]]
    ) -> AwaitableResultTupleWrapper[_F, _T_co]:
        """Deprecated alias for
        [trcks.oop.Wrapper.tap_to_awaitable_result_iterable][].
        """
        return self.tap_to_awaitable_result_iterable(f)  # pragma: no cover

    @deprecated("Use tap_to_awaitable_iterable instead")
    def tap_to_awaitable_tuple(
        self, f: Callable[[_T_co], AwaitableTuple[object]]
    ) -> AwaitableTupleWrapper[_T_co]:
        """Deprecated alias for [trcks.oop.Wrapper.tap_to_awaitable_iterable][]."""
        return self.tap_to_awaitable_iterable(f)  # pragma: no cover

    def tap_to_iterable(
        self, f: Callable[[_T_co], Iterable[object]]
    ) -> TupleWrapper[_T_co]:
        """Apply a side effect returning an [collections.abc.Iterable][] to the
        wrapped object.

        Args:
            f: The side effect to be applied, returning an
                [collections.abc.Iterable][].

        Returns:
            A [trcks.oop.TupleWrapper][] instance with the original wrapped
                object repeated once per item returned by the side effect.

        Example:
            >>> from trcks.oop import Wrapper
            >>> def write_to_disk(n: int) -> tuple[str, str]:
            ...     print(f"Wrote {n} to disk.")
            ...     return "left", "right"
            ...
            >>> Wrapper.construct(3).tap_to_iterable(write_to_disk)
            Wrote 3 to disk.
            TupleWrapper(core=(3, 3))
        """
        return TupleWrapper.construct(self.core).tap_to_iterable(f)

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

    def tap_to_result_iterable(
        self, f: Callable[[_T_co], ResultIterable[_F, object]]
    ) -> ResultTupleWrapper[_F, _T_co]:
        """Apply a synchronous side effect with return type [trcks.ResultIterable][]
        to the wrapped object.

        Args:
            f: The synchronous side effect to be applied.

        Returns:
            A [trcks.oop.ResultTupleWrapper][] instance with

                - *the returned* [trcks.Failure][]
                    if the given side effect returns a [trcks.Failure][] or
                - *the original* [trcks.SuccessIterable][] element repeated once
                    per element in the side effect output if the given side effect
                    returns [trcks.SuccessIterable][].

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
            ... ).tap_to_result_iterable(print_positive_float)
            >>> result_tuple_wrapper_1
            ResultTupleWrapper(core=('failure', 'not positive'))
            >>> result_tuple_wrapper_2 = Wrapper.construct(
            ...     3.5
            ... ).tap_to_result_iterable(print_positive_float)
            Positive float: 3.5
            Positive float: 3.5
            >>> result_tuple_wrapper_2
            ResultTupleWrapper(core=('success', (3.5, 3.5)))
        """
        return ResultTupleWrapper.construct_successes(
            self.core
        ).tap_successes_to_result_iterable(f)

    @deprecated("Use tap_to_result_iterable instead")
    def tap_to_result_tuple(
        self, f: Callable[[_T_co], ResultTuple[_F, object]]
    ) -> ResultTupleWrapper[_F, _T_co]:
        """Deprecated alias for [trcks.oop.Wrapper.tap_to_result_iterable][]."""
        return self.tap_to_result_iterable(f)  # pragma: no cover

    @deprecated("Use tap_to_iterable instead")
    def tap_to_tuple(
        self, f: Callable[[_T_co], tuple[object, ...]]
    ) -> TupleWrapper[_T_co]:
        """Deprecated alias for [trcks.oop.Wrapper.tap_to_iterable][]."""
        return self.tap_to_iterable(f)  # pragma: no cover
