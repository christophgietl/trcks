from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Concatenate, ParamSpec, final

from trcks._typing import TypeVar, deprecated
from trcks.fp.monads import awaitable_tuple as at
from trcks.oop._awaitable_result_tuple_wrapper import AwaitableResultTupleWrapper
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
_P = ParamSpec("_P")
_S = TypeVar("_S")
_T = TypeVar("_T")

_T_co = TypeVar("_T_co", covariant=True)


@final
@dataclass(frozen=True, slots=True)
class AwaitableTupleWrapper(BaseAwaitableWrapper[tuple[_T_co, ...]]):
    """Type-safe and immutable wrapper for [trcks.AwaitableTuple][] objects.

    The wrapped object can be accessed
    via the attribute `trcks.oop.AwaitableTupleWrapper.core`.
    The `trcks.oop.AwaitableTupleWrapper.map*` methods allow method chaining.
    The `trcks.oop.AwaitableTupleWrapper.tap*` methods allow for side effects
    without changing the wrapped tuple.

    Examples:
        >>> import asyncio
        >>> from trcks.oop import AwaitableTupleWrapper
        >>> async def slowly_double(n: int) -> int:
        ...     await asyncio.sleep(0.001)
        ...     return n * 2
        ...
        >>> async def main() -> tuple[int, ...]:
        ...     return await (
        ...         AwaitableTupleWrapper
        ...         .construct_from_iterable((1, 2, 3))
        ...         .map_to_awaitable(slowly_double)
        ...         .core
        ...     )
        ...
        >>> asyncio.run(main())
        (2, 4, 6)
    """

    @staticmethod
    def construct(value: _T, /) -> AwaitableTupleWrapper[_T]:
        """Construct and wrap a [trcks.AwaitableTuple][] object from a value.

        Args:
            value: The value to be wrapped.

        Returns:
            A new [trcks.oop.AwaitableTupleWrapper][] instance with
                the wrapped [trcks.AwaitableTuple][] object.

        Examples:
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
        /,
    ) -> AwaitableTupleWrapper[_T]:
        """Construct and wrap a [trcks.AwaitableTuple][] from an awaitable value.

        Args:
            awtbl: The awaitable value to be wrapped.

        Returns:
            A new [trcks.oop.AwaitableTupleWrapper][] instance with
                the wrapped [trcks.AwaitableTuple][] object.

        Examples:
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
    def construct_from_awaitable_iterable(
        a_it: AwaitableIterable[_T],
        /,
    ) -> AwaitableTupleWrapper[_T]:
        """Construct and wrap a [trcks.AwaitableTuple][] from an
        [trcks.AwaitableIterable][].

        Args:
            a_it: The [trcks.AwaitableIterable][] to be wrapped and converted.

        Returns:
            A new [trcks.oop.AwaitableTupleWrapper][] instance with
                the wrapped [trcks.AwaitableTuple][] object.

        Examples:
            >>> import asyncio
            >>> from trcks import AwaitableIterable
            >>> from trcks.oop import AwaitableTupleWrapper
            >>> async def slowly_get_values() -> list[int]:
            ...     await asyncio.sleep(0.001)
            ...     return [1, 2]
            ...
            >>> awaitable_tuple_wrapper = (
            ...     AwaitableTupleWrapper
            ...     .construct_from_awaitable_iterable(slowly_get_values())
            ... )
            >>> awaitable_tuple_wrapper
            AwaitableTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_tuple_wrapper.core_as_coroutine)
            (1, 2)
        """
        return AwaitableTupleWrapper(at.construct_from_awaitable_iterable(a_it))

    @classmethod
    @deprecated(
        "Use construct_from_awaitable_iterable or the default constructor instead"
    )
    def construct_from_awaitable_tuple(
        cls,
        a_tpl: AwaitableTuple[_T],
        /,
    ) -> AwaitableTupleWrapper[_T]:
        """Deprecated alias for
        [trcks.oop.AwaitableTupleWrapper.construct_from_awaitable_iterable][].
        """
        return cls.construct_from_awaitable_iterable(a_tpl)  # pragma: no cover

    @staticmethod
    def construct_from_iterable(it: Iterable[_T], /) -> AwaitableTupleWrapper[_T]:
        """Construct and wrap a [trcks.AwaitableTuple][] from an iterable.

        Args:
            it: The [collections.abc.Iterable][] to be wrapped and converted.

        Returns:
            A new [trcks.oop.AwaitableTupleWrapper][] instance with
                the wrapped [trcks.AwaitableTuple][] object.

        Examples:
            >>> import asyncio
            >>> from trcks.oop import AwaitableTupleWrapper
            >>> awaitable_tuple_wrapper = (
            ...     AwaitableTupleWrapper
            ...     .construct_from_iterable([1, 2])
            ... )
            >>> awaitable_tuple_wrapper
            AwaitableTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_tuple_wrapper.core_as_coroutine)
            (1, 2)
        """
        return AwaitableTupleWrapper(at.construct_from_iterable(it))

    @classmethod
    @deprecated("Use construct_from_iterable instead")
    def construct_from_tuple(
        cls,
        tpl: tuple[_T, ...],
        /,
    ) -> AwaitableTupleWrapper[_T]:
        """Deprecated alias for construct_from_iterable."""
        return cls.construct_from_iterable(tpl)  # pragma: no cover

    def map(
        self,
        callable_: Callable[Concatenate[_T_co, _P], _T],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AwaitableTupleWrapper[_T]:
        """Apply a synchronous function to each element in the wrapped
        [trcks.AwaitableTuple][] object.

        Args:
            callable_: The synchronous function to be applied to each element.
            *args:
                Positional arguments to be passed to `callable_`.
            **kwargs:
                Keyword arguments to be passed to `callable_`.

        Returns:
            A new [trcks.oop.AwaitableTupleWrapper][] instance with
                the wrapped [trcks.AwaitableTuple][] object containing
                the results of applying the function to each element.

        Examples:
            >>> import asyncio
            >>> from trcks.oop import AwaitableTupleWrapper
            >>> def double_integer(n: int) -> int:
            ...     return n * 2
            ...
            >>> awaitable_tuple_wrapper: AwaitableTupleWrapper[int] = (
            ...     AwaitableTupleWrapper
            ...     .construct_from_iterable((1, 2, 3))
            ...     .map(double_integer)
            ... )
            >>> awaitable_tuple_wrapper
            AwaitableTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_tuple_wrapper.core_as_coroutine)
            (2, 4, 6)
        """
        return AwaitableTupleWrapper(at.map_(callable_, *args, **kwargs)(self.core))

    def map_to_awaitable(
        self,
        callable_: Callable[Concatenate[_T_co, _P], Awaitable[_T]],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AwaitableTupleWrapper[_T]:
        """Apply an asynchronous function to each element in the wrapped
        [trcks.AwaitableTuple][] object.

        Args:
            callable_: The asynchronous function to be applied to each element.
            *args:
                Positional arguments to be passed to `callable_`.
            **kwargs:
                Keyword arguments to be passed to `callable_`.

        Returns:
            A new [trcks.oop.AwaitableTupleWrapper][] instance with
                the wrapped [trcks.AwaitableTuple][] object containing
                the results of applying the function to each element.

        Examples:
            >>> import asyncio
            >>> from trcks.oop import AwaitableTupleWrapper
            >>> async def slowly_add_one(n: int) -> int:
            ...     await asyncio.sleep(0.001)
            ...     return n + 1
            ...
            >>> awaitable_tuple_wrapper: AwaitableTupleWrapper[int] = (
            ...     AwaitableTupleWrapper
            ...     .construct_from_iterable((1, 2))
            ...     .map_to_awaitable(slowly_add_one)
            ... )
            >>> awaitable_tuple_wrapper
            AwaitableTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_tuple_wrapper.core_as_coroutine)
            (2, 3)
        """
        return AwaitableTupleWrapper(
            at.map_to_awaitable(callable_, *args, **kwargs)(self.core)
        )

    def map_to_awaitable_iterable(
        self,
        callable_: Callable[Concatenate[_T_co, _P], AwaitableIterable[_T]],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AwaitableTupleWrapper[_T]:
        """Apply an asynchronous function returning a [trcks.AwaitableIterable][]
        to each element in the wrapped [trcks.AwaitableTuple][] and flatten.

        Args:
            callable_: The asynchronous function to be applied to each element,
                returning a [trcks.AwaitableIterable][].
            *args:
                Positional arguments to be passed to `callable_`.
            **kwargs:
                Keyword arguments to be passed to `callable_`.

        Returns:
            A new [trcks.oop.AwaitableTupleWrapper][] instance with
                the flattened [trcks.AwaitableTuple][] object.

        Examples:
            >>> import asyncio
            >>> from trcks.oop import AwaitableTupleWrapper
            >>> async def slowly_duplicate(n: int) -> tuple[int, int]:
            ...     await asyncio.sleep(0.001)
            ...     return n, n
            ...
            >>> awaitable_tuple_wrapper: AwaitableTupleWrapper[int] = (
            ...     AwaitableTupleWrapper
            ...     .construct_from_iterable((1, 2))
            ...     .map_to_awaitable_iterable(slowly_duplicate)
            ... )
            >>> awaitable_tuple_wrapper
            AwaitableTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_tuple_wrapper.core_as_coroutine)
            (1, 1, 2, 2)
        """
        return AwaitableTupleWrapper(
            at.map_to_awaitable_iterable(callable_, *args, **kwargs)(self.core)
        )

    def map_to_awaitable_result(
        self,
        callable_: Callable[Concatenate[_T_co, _P], AwaitableResult[_F, _S]],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AwaitableResultTupleWrapper[_F, _S]:
        """Apply an asynchronous function with return type [trcks.Result][]
        to each element in the wrapped [trcks.AwaitableTuple][] object.

        Wrapped objects short-circuit on the first [trcks.Failure][].

        Args:
            callable_: The asynchronous function to be applied to each element,
                returning a [trcks.AwaitableResult][].
            *args:
                Positional arguments to be passed to `callable_`.
            **kwargs:
                Keyword arguments to be passed to `callable_`.

        Returns:
            An [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - the first [trcks.Failure][] returned by the function, or
                - a [trcks.SuccessTuple][] if the function returns [trcks.Success][]
                    for all elements.

        Examples:
            >>> import asyncio
            >>> from trcks import Result
            >>> from trcks.oop import AwaitableResultTupleWrapper, AwaitableTupleWrapper
            >>> async def slowly_double_if_positive(n: int) -> Result[str, int]:
            ...     await asyncio.sleep(0.001)
            ...     if n > 0:
            ...         return "success", n * 2
            ...     return "failure", "negative"
            ...
            >>> awaitable_result_tuple_wrapper_1: AwaitableResultTupleWrapper[
            ...     str, int
            ... ] = (
            ...     AwaitableTupleWrapper
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
            ...     AwaitableTupleWrapper
            ...     .construct_from_iterable((1, -1, 2))
            ...     .map_to_awaitable_result(slowly_double_if_positive)
            ... )
            >>> awaitable_result_tuple_wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_result_tuple_wrapper_2.core_as_coroutine)
            ('failure', 'negative')
        """
        return AwaitableResultTupleWrapper(
            at.map_to_awaitable_result(callable_, *args, **kwargs)(self.core)
        )

    def map_to_awaitable_result_iterable(
        self,
        callable_: Callable[Concatenate[_T_co, _P], AwaitableResultIterable[_F, _S]],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AwaitableResultTupleWrapper[_F, _S]:
        """Apply an asynchronous function with return type
        [trcks.AwaitableResultIterable][] to each element in the wrapped
        [trcks.AwaitableTuple][] object and flatten.

        Wrapped objects short-circuit on the first [trcks.Failure][].

        Args:
            callable_: The asynchronous function to be applied to each element,
                returning a [trcks.AwaitableResultIterable][].
            *args:
                Positional arguments to be passed to `callable_`.
            **kwargs:
                Keyword arguments to be passed to `callable_`.

        Returns:
            An [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - the first [trcks.Failure][] returned by the function, or
                - a flattened [trcks.SuccessTuple][] if the function returns
                    [trcks.SuccessTuple][] for all elements.

        Examples:
            >>> import asyncio
            >>> from trcks import ResultTuple
            >>> from trcks.oop import AwaitableResultTupleWrapper, AwaitableTupleWrapper
            >>> async def slowly_expand_if_positive(n: int) -> ResultTuple[str, int]:
            ...     await asyncio.sleep(0.001)
            ...     if n > 0:
            ...         return "success", (n, -n)
            ...     return "failure", "negative"
            ...
            >>> awaitable_result_tuple_wrapper_1: AwaitableResultTupleWrapper[
            ...     str, int
            ... ] = (
            ...     AwaitableTupleWrapper
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
            ...     AwaitableTupleWrapper
            ...     .construct_from_iterable((1, -1, 2))
            ...     .map_to_awaitable_result_iterable(slowly_expand_if_positive)
            ... )
            >>> awaitable_result_tuple_wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_result_tuple_wrapper_2.core_as_coroutine)
            ('failure', 'negative')
        """
        return AwaitableResultTupleWrapper(
            at.map_to_awaitable_result_iterable(callable_, *args, **kwargs)(self.core)
        )

    @deprecated("Use map_to_awaitable_result_iterable instead")
    def map_to_awaitable_result_tuple(
        self,
        callable_: Callable[Concatenate[_T_co, _P], AwaitableResultTuple[_F, _S]],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AwaitableResultTupleWrapper[_F, _S]:
        """Deprecated alias for
        [trcks.oop.AwaitableTupleWrapper.map_to_awaitable_result_iterable][].
        """
        return self.map_to_awaitable_result_iterable(
            callable_, *args, **kwargs
        )  # pragma: no cover

    @deprecated("Use map_to_awaitable_iterable instead")
    def map_to_awaitable_tuple(
        self,
        callable_: Callable[Concatenate[_T_co, _P], AwaitableTuple[_T]],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AwaitableTupleWrapper[_T]:
        """Deprecated alias for
        [trcks.oop.AwaitableTupleWrapper.map_to_awaitable_iterable][].
        """
        return self.map_to_awaitable_iterable(
            callable_, *args, **kwargs
        )  # pragma: no cover

    def map_to_iterable(
        self,
        callable_: Callable[Concatenate[_T_co, _P], Iterable[_T]],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AwaitableTupleWrapper[_T]:
        """Apply a synchronous function returning an [collections.abc.Iterable][]
        to each element in the wrapped [trcks.AwaitableTuple][] object and flatten.

        Args:
            callable_: The synchronous function to be applied to each element,
                returning an [collections.abc.Iterable][].
            *args:
                Positional arguments to be passed to `callable_`.
            **kwargs:
                Keyword arguments to be passed to `callable_`.

        Returns:
            A new [trcks.oop.AwaitableTupleWrapper][] instance with
                the flattened [trcks.AwaitableTuple][] object.

        Examples:
            >>> import asyncio
            >>> from trcks.oop import AwaitableTupleWrapper
            >>> def add_negative(n: int) -> tuple[int, int]:
            ...     return n, -n
            ...
            >>> awaitable_tuple_wrapper: AwaitableTupleWrapper[int] = (
            ...     AwaitableTupleWrapper
            ...     .construct_from_iterable((1, 2))
            ...     .map_to_iterable(add_negative)
            ... )
            >>> awaitable_tuple_wrapper
            AwaitableTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_tuple_wrapper.core_as_coroutine)
            (1, -1, 2, -2)
        """
        return AwaitableTupleWrapper(
            at.map_to_iterable(callable_, *args, **kwargs)(self.core)
        )

    def map_to_result(
        self,
        callable_: Callable[Concatenate[_T_co, _P], Result[_F, _S]],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AwaitableResultTupleWrapper[_F, _S]:
        """Apply a synchronous function with return type [trcks.Result][]
        to each element in the wrapped [trcks.AwaitableTuple][] object.

        Wrapped objects short-circuit on the first [trcks.Failure][].

        Args:
            callable_: The synchronous function to be applied to each element,
                returning a [trcks.Result][].
            *args:
                Positional arguments to be passed to `callable_`.
            **kwargs:
                Keyword arguments to be passed to `callable_`.

        Returns:
            An [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - the first [trcks.Failure][] returned by the function, or
                - a [trcks.SuccessTuple][] with all transformed elements if the
                    function returns [trcks.Success][] for all elements.

        Examples:
            >>> import asyncio
            >>> from trcks import Result
            >>> from trcks.oop import AwaitableResultTupleWrapper, AwaitableTupleWrapper
            >>> def double_if_positive(n: int) -> Result[str, int]:
            ...     if n > 0:
            ...         return "success", n * 2
            ...     return "failure", "negative"
            ...
            >>> awaitable_result_tuple_wrapper_1: AwaitableResultTupleWrapper[
            ...     str, int
            ... ] = (
            ...     AwaitableTupleWrapper
            ...     .construct_from_iterable((1, 2))
            ...     .map_to_result(double_if_positive)
            ... )
            >>> awaitable_result_tuple_wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_result_tuple_wrapper_1.core_as_coroutine)
            ('success', (2, 4))
            >>>
            >>> awaitable_result_tuple_wrapper_2: AwaitableResultTupleWrapper[
            ...     str, int
            ... ] = (
            ...     AwaitableTupleWrapper
            ...     .construct_from_iterable((1, -1, 2))
            ...     .map_to_result(double_if_positive)
            ... )
            >>> awaitable_result_tuple_wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_result_tuple_wrapper_2.core_as_coroutine)
            ('failure', 'negative')
        """
        return AwaitableResultTupleWrapper(
            at.map_to_result(callable_, *args, **kwargs)(self.core)
        )

    def map_to_result_iterable(
        self,
        callable_: Callable[Concatenate[_T_co, _P], ResultIterable[_F, _S]],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AwaitableResultTupleWrapper[_F, _S]:
        """Apply a synchronous function with return type [trcks.ResultIterable][]
        to each element in the wrapped [trcks.AwaitableTuple][] object and flatten.

        Wrapped objects short-circuit on the first [trcks.Failure][].

        Args:
            callable_: The synchronous function to be applied to each element,
                returning a [trcks.ResultIterable][].
            *args:
                Positional arguments to be passed to `callable_`.
            **kwargs:
                Keyword arguments to be passed to `callable_`.

        Returns:
            An [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - the first [trcks.Failure][] returned by the function, or
                - a flattened [trcks.SuccessTuple][] if the function returns
                    [trcks.SuccessTuple][] for all elements.

        Examples:
            >>> import asyncio
            >>> from trcks import ResultTuple
            >>> from trcks.oop import AwaitableResultTupleWrapper, AwaitableTupleWrapper
            >>> def expand_if_positive(n: int) -> ResultTuple[str, int]:
            ...     if n > 0:
            ...         return "success", (n, -n)
            ...     return "failure", "negative"
            ...
            >>> awaitable_result_tuple_wrapper_1: AwaitableResultTupleWrapper[
            ...     str, int
            ... ] = (
            ...     AwaitableTupleWrapper
            ...     .construct_from_iterable((1, 2))
            ...     .map_to_result_iterable(expand_if_positive)
            ... )
            >>> awaitable_result_tuple_wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_result_tuple_wrapper_1.core_as_coroutine)
            ('success', (1, -1, 2, -2))
            >>>
            >>> awaitable_result_tuple_wrapper_2: AwaitableResultTupleWrapper[
            ...     str, int
            ... ] = (
            ...     AwaitableTupleWrapper
            ...     .construct_from_iterable((1, -1, 2))
            ...     .map_to_result_iterable(expand_if_positive)
            ... )
            >>> awaitable_result_tuple_wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_result_tuple_wrapper_2.core_as_coroutine)
            ('failure', 'negative')
        """
        return AwaitableResultTupleWrapper(
            at.map_to_result_iterable(callable_, *args, **kwargs)(self.core)
        )

    @deprecated("Use map_to_result_iterable instead")
    def map_to_result_tuple(
        self,
        callable_: Callable[Concatenate[_T_co, _P], ResultTuple[_F, _S]],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AwaitableResultTupleWrapper[_F, _S]:
        """Deprecated alias for
        [trcks.oop.AwaitableTupleWrapper.map_to_result_iterable][].
        """
        return self.map_to_result_iterable(
            callable_, *args, **kwargs
        )  # pragma: no cover

    @deprecated("Use map_to_iterable instead")
    def map_to_tuple(
        self,
        callable_: Callable[Concatenate[_T_co, _P], tuple[_T, ...]],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AwaitableTupleWrapper[_T]:
        """Deprecated alias for
        [trcks.oop.AwaitableTupleWrapper.map_to_iterable][].
        """
        return self.map_to_iterable(callable_, *args, **kwargs)  # pragma: no cover

    def tap(
        self,
        callable_: Callable[Concatenate[_T_co, _P], object],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AwaitableTupleWrapper[_T_co]:
        """Apply a synchronous side effect to each element in the wrapped
        [trcks.AwaitableTuple][] object.

        Args:
            callable_: The synchronous side effect to be applied to each element.
            *args:
                Positional arguments to be passed to `callable_`.
            **kwargs:
                Keyword arguments to be passed to `callable_`.

        Returns:
            A new [trcks.oop.AwaitableTupleWrapper][] instance with
                the original [trcks.AwaitableTuple][] object.

        Examples:
            >>> import asyncio
            >>> from trcks.oop import AwaitableTupleWrapper
            >>> def log_integer(n: int) -> None:
            ...     print(f"Received: {n}")
            ...
            >>> awaitable_tuple_wrapper: AwaitableTupleWrapper[int] = (
            ...     AwaitableTupleWrapper
            ...     .construct_from_iterable((1, 2))
            ...     .tap(log_integer)
            ... )
            >>> awaitable_tuple_wrapper
            AwaitableTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_tuple_wrapper.core_as_coroutine)
            Received: 1
            Received: 2
            (1, 2)
        """
        return AwaitableTupleWrapper(at.tap(callable_, *args, **kwargs)(self.core))

    def tap_to_awaitable(
        self,
        callable_: Callable[Concatenate[_T_co, _P], Awaitable[object]],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AwaitableTupleWrapper[_T_co]:
        """Apply an asynchronous side effect to each element in the wrapped
        [trcks.AwaitableTuple][] object.

        Args:
            callable_: The asynchronous side effect to be applied to each element.
            *args:
                Positional arguments to be passed to `callable_`.
            **kwargs:
                Keyword arguments to be passed to `callable_`.

        Returns:
            A new [trcks.oop.AwaitableTupleWrapper][] instance with
                the original [trcks.AwaitableTuple][] object.

        Examples:
            >>> import asyncio
            >>> from trcks.oop import AwaitableTupleWrapper
            >>> async def slowly_log(n: int) -> None:
            ...     await asyncio.sleep(0.001)
            ...     print(f"Logged: {n}")
            ...
            >>> awaitable_tuple_wrapper: AwaitableTupleWrapper[int] = (
            ...     AwaitableTupleWrapper
            ...     .construct_from_iterable((1, 2))
            ...     .tap_to_awaitable(slowly_log)
            ... )
            >>> awaitable_tuple_wrapper
            AwaitableTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_tuple_wrapper.core_as_coroutine)
            Logged: 1
            Logged: 2
            (1, 2)
        """
        return AwaitableTupleWrapper(
            at.tap_to_awaitable(callable_, *args, **kwargs)(self.core)
        )

    def tap_to_awaitable_iterable(
        self,
        callable_: Callable[Concatenate[_T_co, _P], AwaitableIterable[object]],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AwaitableTupleWrapper[_T_co]:
        """Apply an asynchronous side effect returning a [trcks.AwaitableIterable][]
        to each element in the wrapped [trcks.AwaitableTuple][] object.

        Args:
            callable_: The asynchronous side effect to be applied to each element,
                returning a [trcks.AwaitableIterable][].
            *args:
                Positional arguments to be passed to `callable_`.
            **kwargs:
                Keyword arguments to be passed to `callable_`.

        Returns:
            A new [trcks.oop.AwaitableTupleWrapper][] instance with
                the original [trcks.AwaitableTuple][] object.

        Examples:
            >>> import asyncio
            >>> from trcks.oop import AwaitableTupleWrapper
            >>> async def slowly_get_divisors(n: int) -> tuple[int, ...]:
            ...     await asyncio.sleep(0.001)
            ...     candidates = range(1, n + 1)
            ...     return tuple(c for c in candidates if n % c == 0)
            ...
            >>> awaitable_tuple_wrapper: AwaitableTupleWrapper[int] = (
            ...     AwaitableTupleWrapper
            ...     .construct_from_iterable((1, 2, 3, 4))
            ...     .tap_to_awaitable_iterable(slowly_get_divisors)
            ... )
            >>> awaitable_tuple_wrapper
            AwaitableTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_tuple_wrapper.core_as_coroutine)
            (1, 2, 2, 3, 3, 4, 4, 4)
        """
        return AwaitableTupleWrapper(
            at.tap_to_awaitable_iterable(callable_, *args, **kwargs)(self.core)
        )

    def tap_to_awaitable_result(
        self,
        callable_: Callable[Concatenate[_T_co, _P], AwaitableResult[_F, object]],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AwaitableResultTupleWrapper[_F, _T_co]:
        """Apply an asynchronous side effect to each element
        in the wrapped [trcks.AwaitableTuple][] object.

        Wrapped objects short-circuit on the first [trcks.Failure][].

        Args:
            callable_: The asynchronous side effect to be applied to each element,
                returning a [trcks.AwaitableResult][].
            *args:
                Positional arguments to be passed to `callable_`.
            **kwargs:
                Keyword arguments to be passed to `callable_`.

        Returns:
            An [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - *the returned* [trcks.Failure][] if the applied side effect
                    returns a [trcks.Failure][] for an element, or
                - *the original* elements from the wrapped
                    [trcks.AwaitableTuple][] object otherwise.

        Examples:
            >>> import asyncio
            >>> from trcks import Result
            >>> from trcks.oop import AwaitableResultTupleWrapper, AwaitableTupleWrapper
            >>> async def slowly_check_if_positive(n: int) -> Result[str, None]:
            ...     await asyncio.sleep(0.001)
            ...     if n > 0:
            ...         return "success", None
            ...     return "failure", "negative"
            ...
            >>> awaitable_result_tuple_wrapper_1: AwaitableResultTupleWrapper[
            ...     str, int
            ... ] = (
            ...     AwaitableTupleWrapper
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
            ...     AwaitableTupleWrapper
            ...     .construct_from_iterable((1, -1, 2))
            ...     .tap_to_awaitable_result(slowly_check_if_positive)
            ... )
            >>> awaitable_result_tuple_wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_result_tuple_wrapper_2.core_as_coroutine)
            ('failure', 'negative')
        """
        return AwaitableResultTupleWrapper(
            at.tap_to_awaitable_result(callable_, *args, **kwargs)(self.core)
        )

    def tap_to_awaitable_result_iterable(
        self,
        callable_: Callable[
            Concatenate[_T_co, _P], AwaitableResultIterable[_F, object]
        ],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AwaitableResultTupleWrapper[_F, _T_co]:
        """Apply an asynchronous side effect to each element
        in the wrapped [trcks.AwaitableTuple][] object,
        repeating each element once per returned side effect element.

        Wrapped objects short-circuit on the first [trcks.Failure][].

        Args:
            callable_: The asynchronous side effect to be applied to each element,
                returning a [trcks.AwaitableResultIterable][].
            *args:
                Positional arguments to be passed to `callable_`.
            **kwargs:
                Keyword arguments to be passed to `callable_`.

        Returns:
            An [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - *the returned* [trcks.Failure][] if the applied side effect
                    returns a [trcks.Failure][] for an element, or
                - *the original* elements from the wrapped
                    [trcks.AwaitableTuple][] object with each element repeated
                    once per side effect output element otherwise, if the
                    applied side effect returns [trcks.SuccessTuple][]
                    for all elements.

        Examples:
            >>> import asyncio
            >>> from trcks import ResultTuple
            >>> from trcks.oop import AwaitableResultTupleWrapper, AwaitableTupleWrapper
            >>> async def slowly_audit(n: int) -> ResultTuple[str, None]:
            ...     await asyncio.sleep(0.001)
            ...     if n > 0:
            ...         return "success", (None, None)
            ...     return "failure", "negative"
            ...
            >>> awaitable_result_tuple_wrapper_1: AwaitableResultTupleWrapper[
            ...     str, int
            ... ] = (
            ...     AwaitableTupleWrapper
            ...     .construct_from_iterable((1, 2))
            ...     .tap_to_awaitable_result_iterable(slowly_audit)
            ... )
            >>> awaitable_result_tuple_wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_result_tuple_wrapper_1.core_as_coroutine)
            ('success', (1, 1, 2, 2))
            >>>
            >>> awaitable_result_tuple_wrapper_2: AwaitableResultTupleWrapper[
            ...     str, int
            ... ] = (
            ...     AwaitableTupleWrapper
            ...     .construct_from_iterable((1, -1, 2))
            ...     .tap_to_awaitable_result_iterable(slowly_audit)
            ... )
            >>> awaitable_result_tuple_wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_result_tuple_wrapper_2.core_as_coroutine)
            ('failure', 'negative')
        """
        return AwaitableResultTupleWrapper(
            at.tap_to_awaitable_result_iterable(callable_, *args, **kwargs)(self.core)
        )

    @deprecated("Use tap_to_awaitable_result_iterable instead")
    def tap_to_awaitable_result_tuple(
        self,
        callable_: Callable[Concatenate[_T_co, _P], AwaitableResultTuple[_F, object]],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AwaitableResultTupleWrapper[_F, _T_co]:
        """Deprecated alias for
        [trcks.oop.AwaitableTupleWrapper.tap_to_awaitable_result_iterable][].
        """
        return self.tap_to_awaitable_result_iterable(
            callable_, *args, **kwargs
        )  # pragma: no cover

    @deprecated("Use tap_to_awaitable_iterable instead")
    def tap_to_awaitable_tuple(
        self,
        callable_: Callable[Concatenate[_T_co, _P], AwaitableTuple[object]],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AwaitableTupleWrapper[_T_co]:
        """Deprecated alias for
        [trcks.oop.AwaitableTupleWrapper.tap_to_awaitable_iterable][].
        """
        return self.tap_to_awaitable_iterable(
            callable_, *args, **kwargs
        )  # pragma: no cover

    def tap_to_iterable(
        self,
        callable_: Callable[Concatenate[_T_co, _P], Iterable[object]],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AwaitableTupleWrapper[_T_co]:
        """Apply a synchronous side effect returning an [collections.abc.Iterable][]
        to each element in the wrapped [trcks.AwaitableTuple][] object.

        Args:
            callable_: The synchronous side effect to be applied to each element,
                returning an [collections.abc.Iterable][].
            *args:
                Positional arguments to be passed to `callable_`.
            **kwargs:
                Keyword arguments to be passed to `callable_`.

        Returns:
            A new [trcks.oop.AwaitableTupleWrapper][] instance with
                the original [trcks.AwaitableTuple][] object.

        Examples:
            >>> import asyncio
            >>> from trcks.oop import AwaitableTupleWrapper
            >>> def get_divisors(n: int) -> tuple[int, ...]:
            ...     candidates = range(1, n + 1)
            ...     return tuple(c for c in candidates if n % c == 0)
            ...
            >>> awaitable_tuple_wrapper: AwaitableTupleWrapper[int] = (
            ...     AwaitableTupleWrapper
            ...     .construct_from_iterable((1, 2, 3, 4))
            ...     .tap_to_iterable(get_divisors)
            ... )
            >>> awaitable_tuple_wrapper
            AwaitableTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_tuple_wrapper.core_as_coroutine)
            (1, 2, 2, 3, 3, 4, 4, 4)
        """
        return AwaitableTupleWrapper(
            at.tap_to_iterable(callable_, *args, **kwargs)(self.core)
        )

    def tap_to_result(
        self,
        callable_: Callable[Concatenate[_T_co, _P], Result[_F, object]],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AwaitableResultTupleWrapper[_F, _T_co]:
        """Apply a synchronous side effect to each element
        in the wrapped [trcks.AwaitableTuple][] object.

        Wrapped objects short-circuit on the first [trcks.Failure][].

        Args:
            callable_: The synchronous side effect to be applied to each element,
                returning a [trcks.Result][].
            *args:
                Positional arguments to be passed to `callable_`.
            **kwargs:
                Keyword arguments to be passed to `callable_`.

        Returns:
            An [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - *the returned* [trcks.Failure][] if the applied side effect
                    returns a [trcks.Failure][] for an element, or
                - *the original* elements from the wrapped
                    [trcks.AwaitableTuple][] object otherwise.

        Examples:
            >>> import asyncio
            >>> from trcks import Result
            >>> from trcks.oop import AwaitableResultTupleWrapper, AwaitableTupleWrapper
            >>> def check_if_positive(n: int) -> Result[str, None]:
            ...     if n > 0:
            ...         return "success", None
            ...     return "failure", "negative"
            ...
            >>> awaitable_result_tuple_wrapper_1: AwaitableResultTupleWrapper[
            ...     str, int
            ... ] = (
            ...     AwaitableTupleWrapper
            ...     .construct_from_iterable((1, 2))
            ...     .tap_to_result(check_if_positive)
            ... )
            >>> awaitable_result_tuple_wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_result_tuple_wrapper_1.core_as_coroutine)
            ('success', (1, 2))
            >>>
            >>> awaitable_result_tuple_wrapper_2: AwaitableResultTupleWrapper[
            ...     str, int
            ... ] = (
            ...     AwaitableTupleWrapper
            ...     .construct_from_iterable((1, -1, 2))
            ...     .tap_to_result(check_if_positive)
            ... )
            >>> awaitable_result_tuple_wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_result_tuple_wrapper_2.core_as_coroutine)
            ('failure', 'negative')
        """
        return AwaitableResultTupleWrapper(
            at.tap_to_result(callable_, *args, **kwargs)(self.core)
        )

    def tap_to_result_iterable(
        self,
        callable_: Callable[Concatenate[_T_co, _P], ResultIterable[_F, object]],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AwaitableResultTupleWrapper[_F, _T_co]:
        """Apply a synchronous side effect to each element
        in the wrapped [trcks.AwaitableTuple][] object,
        repeating each element once per returned side effect element.

        Wrapped objects short-circuit on the first [trcks.Failure][].

        Args:
            callable_: The synchronous side effect to be applied to each element,
                returning a [trcks.ResultIterable][].
            *args:
                Positional arguments to be passed to `callable_`.
            **kwargs:
                Keyword arguments to be passed to `callable_`.

        Returns:
            An [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - *the returned* [trcks.Failure][] if the applied side effect
                    returns a [trcks.Failure][] for an element, or
                - *the original* elements from the wrapped
                    [trcks.AwaitableTuple][] object with each element repeated
                    once per side effect output element otherwise, if the
                    applied side effect returns [trcks.SuccessTuple][]
                    for all elements.

        Examples:
            >>> import asyncio
            >>> from trcks import ResultTuple
            >>> from trcks.oop import AwaitableResultTupleWrapper, AwaitableTupleWrapper
            >>> def audit(n: int) -> ResultTuple[str, None]:
            ...     if n > 0:
            ...         return "success", (None, None)
            ...     return "failure", "negative"
            ...
            >>> awaitable_result_tuple_wrapper_1: AwaitableResultTupleWrapper[
            ...     str, int
            ... ] = (
            ...     AwaitableTupleWrapper
            ...     .construct_from_iterable((1, 2))
            ...     .tap_to_result_iterable(audit)
            ... )
            >>> awaitable_result_tuple_wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_result_tuple_wrapper_1.core_as_coroutine)
            ('success', (1, 1, 2, 2))
            >>>
            >>> awaitable_result_tuple_wrapper_2: AwaitableResultTupleWrapper[
            ...     str, int
            ... ] = (
            ...     AwaitableTupleWrapper
            ...     .construct_from_iterable((1, -1, 2))
            ...     .tap_to_result_iterable(audit)
            ... )
            >>> awaitable_result_tuple_wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_result_tuple_wrapper_2.core_as_coroutine)
            ('failure', 'negative')
        """
        return AwaitableResultTupleWrapper(
            at.tap_to_result_iterable(callable_, *args, **kwargs)(self.core)
        )

    @deprecated("Use tap_to_result_iterable instead")
    def tap_to_result_tuple(
        self,
        callable_: Callable[Concatenate[_T_co, _P], ResultTuple[_F, object]],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AwaitableResultTupleWrapper[_F, _T_co]:
        """Deprecated alias for
        [trcks.oop.AwaitableTupleWrapper.tap_to_result_iterable][].
        """
        return self.tap_to_result_iterable(
            callable_, *args, **kwargs
        )  # pragma: no cover

    @deprecated("Use tap_to_iterable instead")
    def tap_to_tuple(
        self,
        callable_: Callable[Concatenate[_T_co, _P], tuple[object, ...]],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AwaitableTupleWrapper[_T_co]:
        """Deprecated alias for
        [trcks.oop.AwaitableTupleWrapper.tap_to_iterable][].
        """
        return self.tap_to_iterable(callable_, *args, **kwargs)  # pragma: no cover
