from __future__ import annotations

from typing import TYPE_CHECKING

from trcks import (
    AwaitableIterable,
    AwaitableResult,
    AwaitableResultIterable,
    AwaitableResultTuple,
    AwaitableTuple,
)
from trcks._typing import TypeVar, deprecated
from trcks.fp.monads import awaitable as a
from trcks.oop._awaitable_result_tuple_wrapper import AwaitableResultTupleWrapper
from trcks.oop._awaitable_result_wrapper import AwaitableResultWrapper
from trcks.oop._awaitable_tuple_wrapper import AwaitableTupleWrapper
from trcks.oop._base_awaitable_wrapper import BaseAwaitableWrapper

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


class AwaitableWrapper(BaseAwaitableWrapper[_T_co]):
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

    __slots__: tuple[str, ...] = ()

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

    def map_to_awaitable_iterable(
        self, f: Callable[[_T_co], AwaitableIterable[_T]]
    ) -> AwaitableTupleWrapper[_T]:
        """Apply an asynchronous function returning an [collections.abc.Iterable][]
        to the wrapped [collections.abc.Awaitable][] object.

        Args:
            f: The asynchronous function to be applied, returning an awaitable
                [collections.abc.Iterable][].

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
            ...     .map_to_awaitable_iterable(slowly_duplicate)
            ... )
            >>> awaitable_tuple_wrapper
            AwaitableTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_tuple_wrapper.core_as_coroutine)
            (21, 21)
        """
        return AwaitableTupleWrapper(a.map_(tuple)(a.map_to_awaitable(f)(self.core)))

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

    def map_to_awaitable_result_iterable(
        self, f: Callable[[_T_co], AwaitableResultIterable[_F, _S]]
    ) -> AwaitableResultTupleWrapper[_F, _S]:
        """Apply an asynchronous function with return type
        [trcks.AwaitableResultIterable][] to the wrapped
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
            ...     .map_to_awaitable_result_iterable(validate)
            ... )
            >>> wrapper
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper.core_as_coroutine)
            ('success', (5.0, 10.0))
        """
        return AwaitableResultTupleWrapper.construct_successes_from_awaitable(
            self.core
        ).map_successes_to_awaitable_result_iterable(f)

    @deprecated("Use map_to_awaitable_result_iterable instead")
    def map_to_awaitable_result_tuple(
        self, f: Callable[[_T_co], AwaitableResultTuple[_F, _S]]
    ) -> AwaitableResultTupleWrapper[_F, _S]:
        """Deprecated alias for
        [trcks.oop.AwaitableWrapper.map_to_awaitable_result_iterable][].
        """
        return self.map_to_awaitable_result_iterable(f)  # pragma: no cover

    @deprecated("Use map_to_awaitable_iterable instead")
    def map_to_awaitable_tuple(
        self, f: Callable[[_T_co], AwaitableTuple[_T]]
    ) -> AwaitableTupleWrapper[_T]:
        """Deprecated alias for
        [trcks.oop.AwaitableWrapper.map_to_awaitable_iterable][].
        """
        return self.map_to_awaitable_iterable(f)  # pragma: no cover

    def map_to_iterable(
        self, f: Callable[[_T_co], Iterable[_T]]
    ) -> AwaitableTupleWrapper[_T]:
        """Apply a synchronous function returning an [collections.abc.Iterable][]
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
            ...     .map_to_iterable(lambda n: (n, -n))
            ... )
            >>> awaitable_tuple_wrapper
            AwaitableTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_tuple_wrapper.core_as_coroutine)
            (3, -3)
        """
        return AwaitableTupleWrapper(a.map_(tuple)(a.map_(f)(self.core)))

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

    def map_to_result_iterable(
        self, f: Callable[[_T_co], ResultIterable[_F, _S]]
    ) -> AwaitableResultTupleWrapper[_F, _S]:
        """Apply a synchronous function with return type [trcks.ResultIterable][]
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
            >>> wrapper = AwaitableWrapper.construct(5.0).map_to_result_iterable(
            ...     validate
            ... )
            >>> wrapper
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper.core_as_coroutine)
            ('success', (5.0, 10.0))
        """
        return AwaitableResultTupleWrapper.construct_successes_from_awaitable(
            self.core
        ).map_successes_to_result_iterable(f)

    @deprecated("Use map_to_result_iterable instead")
    def map_to_result_tuple(
        self, f: Callable[[_T_co], ResultTuple[_F, _S]]
    ) -> AwaitableResultTupleWrapper[_F, _S]:
        """Deprecated alias for
        [trcks.oop.AwaitableWrapper.map_to_result_iterable][].
        """
        return self.map_to_result_iterable(f)  # pragma: no cover

    @deprecated("Use map_to_iterable instead")
    def map_to_tuple(
        self, f: Callable[[_T_co], tuple[_T, ...]]
    ) -> AwaitableTupleWrapper[_T]:
        """Deprecated alias for
        [trcks.oop.AwaitableWrapper.map_to_iterable][].
        """
        return self.map_to_iterable(f)  # pragma: no cover

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

    def tap_to_awaitable_iterable(
        self, f: Callable[[_T_co], AwaitableIterable[object]]
    ) -> AwaitableTupleWrapper[_T_co]:
        """Apply an asynchronous side effect returning a [trcks.AwaitableIterable][]
        to the wrapped [collections.abc.Awaitable][] object.

        Args:
            f: The asynchronous side effect to be applied,
                returning a [trcks.AwaitableIterable][].

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
            ...     .tap_to_awaitable_iterable(slowly_duplicate_with_log)
            ... )
            >>> awaitable_tuple_wrapper
            AwaitableTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_tuple_wrapper.core_as_coroutine)
            Processing: 21
            (21, 21)
        """
        return AwaitableTupleWrapper.construct_from_awaitable(
            self.core
        ).tap_to_awaitable_iterable(f)

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

    def tap_to_awaitable_result_iterable(
        self, f: Callable[[_T_co], AwaitableResultIterable[_F, object]]
    ) -> AwaitableResultTupleWrapper[_F, _T_co]:
        """Apply an asynchronous side effect with return type
        [trcks.AwaitableResultIterable][] to the wrapped
        [collections.abc.Awaitable][] object.

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
            ... ).tap_to_awaitable_result_iterable(write_twice)
            >>> wrapper
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> result = asyncio.run(wrapper.core_as_coroutine)
            Wrote 'Hello, world!' twice.
            >>> result
            ('success', ('Hello, world!', 'Hello, world!'))
        """
        return AwaitableResultTupleWrapper.construct_successes_from_awaitable(
            self.core
        ).tap_successes_to_awaitable_result_iterable(f)

    @deprecated("Use tap_to_awaitable_result_iterable instead")
    def tap_to_awaitable_result_tuple(
        self, f: Callable[[_T_co], AwaitableResultTuple[_F, object]]
    ) -> AwaitableResultTupleWrapper[_F, _T_co]:
        """Deprecated alias for
        [trcks.oop.AwaitableWrapper.tap_to_awaitable_result_iterable][].
        """
        return self.tap_to_awaitable_result_iterable(f)  # pragma: no cover

    @deprecated("Use tap_to_awaitable_iterable instead")
    def tap_to_awaitable_tuple(
        self, f: Callable[[_T_co], AwaitableTuple[object]]
    ) -> AwaitableTupleWrapper[_T_co]:
        """Deprecated alias for
        [trcks.oop.AwaitableWrapper.tap_to_awaitable_iterable][].
        """
        return self.tap_to_awaitable_iterable(f)  # pragma: no cover

    def tap_to_iterable(
        self, f: Callable[[_T_co], Iterable[object]]
    ) -> AwaitableTupleWrapper[_T_co]:
        """Apply a synchronous side effect returning an [collections.abc.Iterable][]
        to the wrapped [collections.abc.Awaitable][] object.

        Args:
            f: The synchronous side effect to be applied,
                returning an [collections.abc.Iterable][].

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
            ...     .tap_to_iterable(duplicate_with_log)
            ... )
            >>> awaitable_tuple_wrapper
            AwaitableTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_tuple_wrapper.core_as_coroutine)
            Processing: 42
            (42, 42)
        """
        return AwaitableTupleWrapper.construct_from_awaitable(
            self.core
        ).tap_to_iterable(f)

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

    def tap_to_result_iterable(
        self, f: Callable[[_T_co], ResultIterable[_F, object]]
    ) -> AwaitableResultTupleWrapper[_F, _T_co]:
        """Apply a synchronous side effect with return type [trcks.ResultIterable][]
        to the wrapped [collections.abc.Awaitable][] object.

        Args:
            f: The synchronous side effect to be applied.

        Returns:
            A [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - *the returned* [trcks.Failure][]
                    if the given side effect returns a [trcks.Failure][] or
                - *the original* wrapped object repeated once per element
                    in the side effect output if the given side effect
                    returns [trcks.SuccessIterable][].

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
            ... ).tap_to_result_iterable(write_twice)
            >>> wrapper
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> result = asyncio.run(wrapper.core_as_coroutine)
            Wrote 'Hello, world!' twice.
            >>> result
            ('success', ('Hello, world!', 'Hello, world!'))
        """
        return AwaitableResultTupleWrapper.construct_successes_from_awaitable(
            self.core
        ).tap_successes_to_result_iterable(f)

    @deprecated("Use tap_to_result_iterable instead")
    def tap_to_result_tuple(
        self, f: Callable[[_T_co], ResultTuple[_F, object]]
    ) -> AwaitableResultTupleWrapper[_F, _T_co]:
        """Deprecated alias for
        [trcks.oop.AwaitableWrapper.tap_to_result_iterable][].
        """
        return self.tap_to_result_iterable(f)  # pragma: no cover

    @deprecated("Use tap_to_iterable instead")
    def tap_to_tuple(
        self, f: Callable[[_T_co], tuple[object, ...]]
    ) -> AwaitableTupleWrapper[_T_co]:
        """Deprecated alias for
        [trcks.oop.AwaitableWrapper.tap_to_iterable][].
        """
        return self.tap_to_iterable(f)  # pragma: no cover
