from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Concatenate, ParamSpec, final

from trcks import ResultTuple
from trcks._typing import Never, TypeVar, deprecated
from trcks.fp.monads import awaitable_result_tuple as art
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
    )

__docformat__ = "google"

_F = TypeVar("_F")
_P = ParamSpec("_P")
_S = TypeVar("_S")

_F_default = TypeVar("_F_default", default=Never)
_S_default = TypeVar("_S_default", default=Never)

_F_default_co = TypeVar("_F_default_co", covariant=True, default=Never)
_S_default_co = TypeVar("_S_default_co", covariant=True, default=Never)


@final
@dataclass(frozen=True, slots=True)
class AwaitableResultTupleWrapper(
    BaseAwaitableWrapper[ResultTuple[_F_default_co, _S_default_co]]
):
    """Type-safe and immutable wrapper for
    [`AwaitableResultTuple`][trcks.AwaitableResultTuple] objects.

    The wrapped object can be accessed
    via the attribute `trcks.oop.AwaitableResultTupleWrapper.core`.
    The `trcks.oop.AwaitableResultTupleWrapper.map*` methods allow method chaining.
    The `trcks.oop.AwaitableResultTupleWrapper.tap*` methods allow for side effects
    without changing the wrapped [`ResultTuple`][trcks.ResultTuple].

    Examples:
        >>> from trcks.oop import AwaitableResultTupleWrapper
        >>> import asyncio
        >>> from trcks import Result
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
        ...         .map_successes_to_iterable(lambda n: (n, -n))
        ...         .core
        ...     )
        ...
        >>> asyncio.run(main())
        Processed: 6
        ('success', (6, -6))
    """

    @staticmethod
    def construct_failure(value: _F, /) -> AwaitableResultTupleWrapper[_F, Never]:
        """Construct and wrap an awaitable [`Failure`][trcks.Failure] object from a
        value.

        Args:
            value: The value to be wrapped.

        Returns:
            A new [`AwaitableResultTupleWrapper`][trcks.oop.AwaitableResultTupleWrapper]
                instance with
                the wrapped [`AwaitableResultTuple`][trcks.AwaitableResultTuple] object.

        Examples:
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
        /,
    ) -> AwaitableResultTupleWrapper[_F, Never]:
        """Construct and wrap an awaitable [`Failure`][trcks.Failure] from an awaitable
        value.

        Args:
            awtbl: The awaitable value to be wrapped.

        Returns:
            A new [`AwaitableResultTupleWrapper`][trcks.oop.AwaitableResultTupleWrapper]
                instance with
                the wrapped [`AwaitableResultTuple`][trcks.AwaitableResultTuple] object.

        Examples:
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
        /,
    ) -> AwaitableResultTupleWrapper[_F, _S]:
        """Construct and wrap an [`AwaitableResultTuple`][trcks.AwaitableResultTuple]
        from an [`AwaitableResult`][trcks.AwaitableResult].

        The success payload is wrapped in a single-element tuple.

        Args:
            a_rslt: The [`AwaitableResult`][trcks.AwaitableResult] object to be
                converted.

        Returns:
            A new [`AwaitableResultTupleWrapper`][trcks.oop.AwaitableResultTupleWrapper]
                instance where
                the success payload is wrapped in a single-element tuple,
                or the original failure is preserved.

        Examples:
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
    def construct_from_awaitable_result_iterable(
        a_r_it: AwaitableResultIterable[_F, _S],
        /,
    ) -> AwaitableResultTupleWrapper[_F, _S]:
        """Construct and wrap an [`AwaitableResultTuple`][trcks.AwaitableResultTuple]
        from an [`AwaitableResultIterable`][trcks.AwaitableResultIterable].

        Args:
            a_r_it: The [`AwaitableResultIterable`][trcks.AwaitableResultIterable]
                object to be converted.

        Returns:
            A new [`AwaitableResultTupleWrapper`][trcks.oop.AwaitableResultTupleWrapper]
                instance where
                the success payload is converted to a tuple,
                or the original failure is preserved.

        Examples:
            >>> import asyncio
            >>> from trcks import ResultIterable
            >>> from trcks.oop import AwaitableResultTupleWrapper
            >>> async def slowly_read_from_disk() -> ResultIterable[str, int]:
            ...     await asyncio.sleep(0.001)
            ...     return "success", [1, 2]
            ...
            >>> wrapper = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_from_awaitable_result_iterable(slowly_read_from_disk())
            ... )
            >>> wrapper
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper.core_as_coroutine)
            ('success', (1, 2))
        """
        return AwaitableResultTupleWrapper(
            art.construct_from_awaitable_result_iterable(a_r_it)
        )

    @classmethod
    @deprecated("Use construct_from_awaitable_result_iterable instead")
    def construct_from_awaitable_result_tuple(
        cls,
        a_r_tpl: AwaitableResultTuple[_F, _S],
        /,
    ) -> AwaitableResultTupleWrapper[_F, _S]:
        """Deprecated alias for
        [`construct_from_awaitable_result_iterable`][trcks.oop.AwaitableResultTupleWrapper.construct_from_awaitable_result_iterable].
        """
        return cls.construct_from_awaitable_result_iterable(a_r_tpl)  # pragma: no cover

    @staticmethod
    def construct_from_result(
        rslt: Result[_F_default, _S_default],
        /,
    ) -> AwaitableResultTupleWrapper[_F_default, _S_default]:
        """Construct and wrap an [`AwaitableResultTuple`][trcks.AwaitableResultTuple]
        from a [`Result`][trcks.Result].

        The success payload is wrapped in a single-element tuple.

        Args:
            rslt: The [`Result`][trcks.Result] object to be converted.

        Returns:
            A new [`AwaitableResultTupleWrapper`][trcks.oop.AwaitableResultTupleWrapper]
                instance where
                the success payload is wrapped in a single-element tuple,
                or the original failure is preserved.

        Examples:
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
    def construct_from_result_iterable(
        it: ResultIterable[_F_default, _S_default],
        /,
    ) -> AwaitableResultTupleWrapper[_F_default, _S_default]:
        """Wrap a [`ResultIterable`][trcks.ResultIterable] object and convert it into an
        [`AwaitableResultTuple`][trcks.AwaitableResultTuple].

        Args:
            it: The [`ResultIterable`][trcks.ResultIterable] object to be wrapped and
                converted.

        Returns:
            A new [`AwaitableResultTupleWrapper`][trcks.oop.AwaitableResultTupleWrapper]
                instance with
                the wrapped [`AwaitableResultTuple`][trcks.AwaitableResultTuple] object.

        Examples:
            >>> import asyncio
            >>> from trcks.oop import AwaitableResultTupleWrapper
            >>> wrapper = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_from_result_iterable(("success", [1, 2]))
            ... )
            >>> wrapper
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper.core_as_coroutine)
            ('success', (1, 2))
        """
        return AwaitableResultTupleWrapper(art.construct_from_result_iterable(it))

    @classmethod
    @deprecated("Use construct_from_result_iterable instead")
    def construct_from_result_tuple(
        cls,
        r_tpl: ResultTuple[_F_default, _S_default],
        /,
    ) -> AwaitableResultTupleWrapper[_F_default, _S_default]:
        """Deprecated alias for
        [`construct_from_result_iterable`][trcks.oop.AwaitableResultTupleWrapper.construct_from_result_iterable].
        """
        return cls.construct_from_result_iterable(r_tpl)  # pragma: no cover

    @staticmethod
    def construct_successes(value: _S, /) -> AwaitableResultTupleWrapper[Never, _S]:
        """Construct and wrap an awaitable [`SuccessTuple`][trcks.SuccessTuple] from a
        value.

        Args:
            value: The value to be wrapped in a single-element tuple.

        Returns:
            A new [`AwaitableResultTupleWrapper`][trcks.oop.AwaitableResultTupleWrapper]
                instance with
                the wrapped [`AwaitableResultTuple`][trcks.AwaitableResultTuple] object.

        Examples:
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
        /,
    ) -> AwaitableResultTupleWrapper[Never, _S]:
        """Construct and wrap an awaitable [`SuccessTuple`][trcks.SuccessTuple] from an
        awaitable value.

        Args:
            awtbl: The awaitable value to be wrapped in a single-element tuple.

        Returns:
            A new [`AwaitableResultTupleWrapper`][trcks.oop.AwaitableResultTupleWrapper]
                instance with
                the wrapped [`AwaitableResultTuple`][trcks.AwaitableResultTuple] object.

        Examples:
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
    def construct_successes_from_awaitable_iterable(
        a_it: AwaitableIterable[_S],
        /,
    ) -> AwaitableResultTupleWrapper[Never, _S]:
        """Construct and wrap an awaitable [`SuccessTuple`][trcks.SuccessTuple] from an
        [`AwaitableIterable`][trcks.AwaitableIterable].

        Args:
            a_it: The [`AwaitableIterable`][trcks.AwaitableIterable] object to be
                wrapped and converted.

        Returns:
            A new [`AwaitableResultTupleWrapper`][trcks.oop.AwaitableResultTupleWrapper]
                instance with
                the wrapped [`AwaitableResultTuple`][trcks.AwaitableResultTuple] object.

        Examples:
            >>> import asyncio
            >>> from trcks import AwaitableIterable
            >>> from trcks.fp.monads import awaitable as a
            >>> from trcks.oop import AwaitableResultTupleWrapper
            >>> a_it: AwaitableIterable[int] = a.construct([1, 2])
            >>> wrapper = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_successes_from_awaitable_iterable(a_it)
            ... )
            >>> wrapper
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper.core_as_coroutine)
            ('success', (1, 2))
        """
        return AwaitableResultTupleWrapper(
            art.construct_successes_from_awaitable_iterable(a_it)
        )

    @classmethod
    @deprecated("Use construct_successes_from_awaitable_iterable instead")
    def construct_successes_from_awaitable_tuple(
        cls,
        a_tpl: AwaitableTuple[_S],
        /,
    ) -> AwaitableResultTupleWrapper[Never, _S]:
        """Deprecated alias for
        [`construct_successes_from_awaitable_iterable`][trcks.oop.AwaitableResultTupleWrapper.construct_successes_from_awaitable_iterable].
        """
        return cls.construct_successes_from_awaitable_iterable(
            a_tpl
        )  # pragma: no cover

    @staticmethod
    def construct_successes_from_iterable(
        it: Iterable[_S],
        /,
    ) -> AwaitableResultTupleWrapper[Never, _S]:
        """Construct and wrap an awaitable [`SuccessTuple`][trcks.SuccessTuple] from an
        iterable.

        Args:
            it: The [`Iterable`][collections.abc.Iterable] to be wrapped and converted.

        Returns:
            A new [`AwaitableResultTupleWrapper`][trcks.oop.AwaitableResultTupleWrapper]
                instance with
                the wrapped [`AwaitableResultTuple`][trcks.AwaitableResultTuple] object.

        Examples:
            >>> import asyncio
            >>> from trcks.oop import AwaitableResultTupleWrapper
            >>> wrapper = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_successes_from_iterable([1, 2])
            ... )
            >>> wrapper
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper.core_as_coroutine)
            ('success', (1, 2))
        """
        return AwaitableResultTupleWrapper(art.construct_successes_from_iterable(it))

    @classmethod
    @deprecated("Use construct_successes_from_iterable instead")
    def construct_successes_from_tuple(
        cls,
        tpl: tuple[_S, ...],
        /,
    ) -> AwaitableResultTupleWrapper[Never, _S]:
        """Deprecated alias for
        [`construct_successes_from_iterable`][trcks.oop.AwaitableResultTupleWrapper.construct_successes_from_iterable].
        """
        return cls.construct_successes_from_iterable(tpl)  # pragma: no cover

    def map_failure(
        self,
        callable_: Callable[Concatenate[_F_default_co, _P], _F],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AwaitableResultTupleWrapper[_F, _S_default_co]:
        """Apply a synchronous function to the wrapped [`Failure`][trcks.Failure]
        object.

        Wrapped [`SuccessTuple`][trcks.SuccessTuple] objects are passed on unchanged.

        Args:
            callable_: The synchronous function to be applied.
            *args:
                Positional arguments to be passed to `callable_`.
            **kwargs:
                Keyword arguments to be passed to `callable_`.

        Returns:
            A new [`AwaitableResultTupleWrapper`][trcks.oop.AwaitableResultTupleWrapper]
                instance with

                - the result of the function application if
                    the original [`AwaitableResultTuple`][trcks.AwaitableResultTuple] is
                    a failure, or
                - the original [`AwaitableResultTuple`][trcks.AwaitableResultTuple] if
                  it is a success.

        Examples:
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
            ...     .construct_successes_from_iterable((1, 2))
            ...     .map_failure(lambda e: f"err: {e}")
            ... )
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('success', (1, 2))
        """
        return AwaitableResultTupleWrapper(
            art.map_failure(callable_, *args, **kwargs)(self.core)
        )

    def map_failure_to_awaitable(
        self,
        callable_: Callable[Concatenate[_F_default_co, _P], Awaitable[_F]],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AwaitableResultTupleWrapper[_F, _S_default_co]:
        """Apply an asynchronous function to the wrapped [`Failure`][trcks.Failure]
        object.

        Wrapped [`SuccessTuple`][trcks.SuccessTuple] objects are passed on unchanged.

        Args:
            callable_: The asynchronous function to be applied.
            *args:
                Positional arguments to be passed to `callable_`.
            **kwargs:
                Keyword arguments to be passed to `callable_`.

        Returns:
            A new [`AwaitableResultTupleWrapper`][trcks.oop.AwaitableResultTupleWrapper]
                instance with

                - the result of the function application if
                    the original [`AwaitableResultTuple`][trcks.AwaitableResultTuple] is
                    a failure, or
                - the original [`AwaitableResultTuple`][trcks.AwaitableResultTuple] if
                  it is a success.

        Examples:
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
            ...     .construct_successes_from_iterable((1, 2))
            ...     .map_failure_to_awaitable(_slowly_add_prefix)
            ... )
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('success', (1, 2))
        """
        return AwaitableResultTupleWrapper(
            art.map_failure_to_awaitable(callable_, *args, **kwargs)(self.core)
        )

    def map_failure_to_awaitable_iterable(
        self,
        callable_: Callable[Concatenate[_F_default_co, _P], AwaitableIterable[_S]],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AwaitableResultTupleWrapper[Never, _S_default_co | _S]:
        """Apply an asynchronous function returning an
        [`Iterable`][collections.abc.Iterable] to the wrapped [`Failure`][trcks.Failure]
        object.

        Wrapped [`SuccessTuple`][trcks.SuccessTuple] objects are passed on unchanged.

        Args:
            callable_: The asynchronous function returning an
                [`Iterable`][collections.abc.Iterable] to be applied.
            *args:
                Positional arguments to be passed to `callable_`.
            **kwargs:
                Keyword arguments to be passed to `callable_`.

        Returns:
            A new [`AwaitableResultTupleWrapper`][trcks.oop.AwaitableResultTupleWrapper]
                instance with

                - an [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple] containing
                  the result of the function application if the original
                  [`AwaitableResultTuple`][trcks.AwaitableResultTuple] is a failure, or
                - the original [`AwaitableResultTuple`][trcks.AwaitableResultTuple] if
                  it is a success.

        Examples:
            >>> import asyncio
            >>> from trcks.oop import AwaitableResultTupleWrapper
            >>> async def _slowly_recover_from_failure(
            ...     description: str,
            ... ) -> list[int]:
            ...     await asyncio.sleep(0.001)
            ...     if description == "not found":
            ...         return [0]
            ...     return []
            ...
            >>> wrapper_1 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_failure("not found")
            ...     .map_failure_to_awaitable_iterable(_slowly_recover_from_failure)
            ... )
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('success', (0,))
            >>>
            >>> wrapper_2 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_failure("fatal")
            ...     .map_failure_to_awaitable_iterable(_slowly_recover_from_failure)
            ... )
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('success', ())
            >>>
            >>> wrapper_3 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_successes_from_iterable([1, 2])
            ...     .map_failure_to_awaitable_iterable(_slowly_recover_from_failure)
            ... )
            >>> wrapper_3
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_3.core_as_coroutine)
            ('success', (1, 2))
        """
        mapped_callable: Callable[
            [AwaitableResultTuple[_F_default_co, _S_default_co]],
            AwaitableResultTuple[Never, _S_default_co | _S],
        ] = art.map_failure_to_awaitable_iterable(callable_, *args, **kwargs)
        return AwaitableResultTupleWrapper(mapped_callable(self.core))

    def map_failure_to_awaitable_result(
        self,
        callable_: Callable[Concatenate[_F_default_co, _P], AwaitableResult[_F, _S]],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AwaitableResultTupleWrapper[_F, _S_default_co | _S]:
        """Apply an asynchronous function with return type
        [`AwaitableResult`][trcks.AwaitableResult] to the wrapped
        [`Failure`][trcks.Failure] object.

        Wrapped [`SuccessTuple`][trcks.SuccessTuple] objects are passed on unchanged.

        Args:
            callable_: The asynchronous function to be applied.
            *args:
                Positional arguments to be passed to `callable_`.
            **kwargs:
                Keyword arguments to be passed to `callable_`.

        Returns:
            A new [`AwaitableResultTupleWrapper`][trcks.oop.AwaitableResultTupleWrapper]
                instance with

                - the result of the function application if
                    the original [`AwaitableResultTuple`][trcks.AwaitableResultTuple] is
                    a failure, or
                - the original [`AwaitableResultTuple`][trcks.AwaitableResultTuple] if
                  it is a success.

        Examples:
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
            ...     .map_failure_to_awaitable_result(_slowly_recover_from_not_found)
            ... )
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('success', (0,))
            >>>
            >>> wrapper_2 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_failure("fatal")
            ...     .map_failure_to_awaitable_result(_slowly_recover_from_not_found)
            ... )
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('failure', 'fatal')
            >>>
            >>> wrapper_3 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_successes_from_iterable([1, 2])
            ...     .map_failure_to_awaitable_result(_slowly_recover_from_not_found)
            ... )
            >>> wrapper_3
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_3.core_as_coroutine)
            ('success', (1, 2))
        """
        return AwaitableResultTupleWrapper(
            art.map_failure_to_awaitable_result(callable_, *args, **kwargs)(self.core)
        )

    def map_failure_to_awaitable_result_iterable(
        self,
        callable_: Callable[
            Concatenate[_F_default_co, _P], AwaitableResultIterable[_F, _S]
        ],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AwaitableResultTupleWrapper[_F, _S_default_co | _S]:
        """Apply an asynchronous function with return type
        [`AwaitableResultIterable`][trcks.AwaitableResultIterable] to the wrapped
        [`Failure`][trcks.Failure] object.

        Wrapped [`SuccessTuple`][trcks.SuccessTuple] objects are passed on unchanged.

        Args:
            callable_: The asynchronous function to be applied.
            *args:
                Positional arguments to be passed to `callable_`.
            **kwargs:
                Keyword arguments to be passed to `callable_`.

        Returns:
            A new [`AwaitableResultTupleWrapper`][trcks.oop.AwaitableResultTupleWrapper]
                instance with

                - the result of the function application if
                    the original [`AwaitableResultTuple`][trcks.AwaitableResultTuple] is
                    a failure, or
                - the original [`AwaitableResultTuple`][trcks.AwaitableResultTuple] if
                  it is a success.

        Examples:
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
            ...     .map_failure_to_awaitable_result_iterable(
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
            ...     .map_failure_to_awaitable_result_iterable(
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
            ...     .construct_successes_from_iterable((1, 2))
            ...     .map_failure_to_awaitable_result_iterable(
            ...         _slowly_recover_from_not_found,
            ...     )
            ... )
            >>> wrapper_3
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_3.core_as_coroutine)
            ('success', (1, 2))
        """
        return AwaitableResultTupleWrapper(
            art.map_failure_to_awaitable_result_iterable(callable_, *args, **kwargs)(
                self.core
            )
        )

    @deprecated("Use map_failure_to_awaitable_result_iterable instead")
    def map_failure_to_awaitable_result_tuple(
        self,
        callable_: Callable[
            Concatenate[_F_default_co, _P], AwaitableResultTuple[_F, _S]
        ],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AwaitableResultTupleWrapper[_F, _S_default_co | _S]:
        """Deprecated alias for
        [`map_failure_to_awaitable_result_iterable`][trcks.oop.AwaitableResultTupleWrapper.map_failure_to_awaitable_result_iterable].
        """
        return self.map_failure_to_awaitable_result_iterable(
            callable_, *args, **kwargs
        )  # pragma: no cover

    @deprecated("Use map_failure_to_awaitable_iterable instead")
    def map_failure_to_awaitable_tuple(
        self,
        callable_: Callable[Concatenate[_F_default_co, _P], AwaitableTuple[_S]],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AwaitableResultTupleWrapper[Never, _S_default_co | _S]:
        """Deprecated alias for
        [`map_failure_to_awaitable_iterable`][trcks.oop.AwaitableResultTupleWrapper.map_failure_to_awaitable_iterable].
        """
        return self.map_failure_to_awaitable_iterable(
            callable_, *args, **kwargs
        )  # pragma: no cover

    def map_failure_to_iterable(
        self,
        callable_: Callable[Concatenate[_F_default_co, _P], Iterable[_S]],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AwaitableResultTupleWrapper[Never, _S_default_co | _S]:
        """Apply a synchronous function returning an
        [`Iterable`][collections.abc.Iterable] to the wrapped [`Failure`][trcks.Failure]
        object.

        Wrapped [`SuccessTuple`][trcks.SuccessTuple] objects are passed on unchanged.

        Args:
            callable_: The synchronous function returning an
                [`Iterable`][collections.abc.Iterable] to be applied.
            *args:
                Positional arguments to be passed to `callable_`.
            **kwargs:
                Keyword arguments to be passed to `callable_`.

        Returns:
            A new [`AwaitableResultTupleWrapper`][trcks.oop.AwaitableResultTupleWrapper]
                instance with

                - an [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple] containing
                  the result of the function application if the original
                  [`AwaitableResultTuple`][trcks.AwaitableResultTuple] is a failure, or
                - the original [`AwaitableResultTuple`][trcks.AwaitableResultTuple] if
                  it is a success.

        Examples:
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
            ...     .map_failure_to_iterable(_recover_from_not_found)
            ... )
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('success', (0,))
            >>>
            >>> wrapper_2 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_failure("fatal")
            ...     .map_failure_to_iterable(_recover_from_not_found)
            ... )
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('success', ())
            >>>
            >>> wrapper_3 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_successes_from_iterable((1, 2))
            ...     .map_failure_to_iterable(_recover_from_not_found)
            ... )
            >>> wrapper_3
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_3.core_as_coroutine)
            ('success', (1, 2))
        """
        mapped_callable: Callable[
            [AwaitableResultTuple[_F_default_co, _S_default_co]],
            AwaitableResultTuple[Never, _S_default_co | _S],
        ] = art.map_failure_to_iterable(callable_, *args, **kwargs)
        return AwaitableResultTupleWrapper(mapped_callable(self.core))

    def map_failure_to_result(
        self,
        callable_: Callable[Concatenate[_F_default_co, _P], Result[_F, _S]],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AwaitableResultTupleWrapper[_F, _S_default_co | _S]:
        """Apply a synchronous function with return type [`Result`][trcks.Result]
        to the wrapped [`Failure`][trcks.Failure] object.

        Wrapped [`SuccessTuple`][trcks.SuccessTuple] objects are passed on unchanged.

        Args:
            callable_: The synchronous function to be applied.
            *args:
                Positional arguments to be passed to `callable_`.
            **kwargs:
                Keyword arguments to be passed to `callable_`.

        Returns:
            A new [`AwaitableResultTupleWrapper`][trcks.oop.AwaitableResultTupleWrapper]
                instance with

                - the result of the function application if
                    the original [`AwaitableResultTuple`][trcks.AwaitableResultTuple] is
                    a failure, or
                - the original [`AwaitableResultTuple`][trcks.AwaitableResultTuple] if
                  it is a success.

        Examples:
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
            ...     .construct_successes_from_iterable((1, 2))
            ...     .map_failure_to_result(_recover_from_not_found)
            ... )
            >>> wrapper_3
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_3.core_as_coroutine)
            ('success', (1, 2))
        """
        return AwaitableResultTupleWrapper(
            art.map_failure_to_result(callable_, *args, **kwargs)(self.core)
        )

    def map_failure_to_result_iterable(
        self,
        callable_: Callable[Concatenate[_F_default_co, _P], ResultIterable[_F, _S]],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AwaitableResultTupleWrapper[_F, _S_default_co | _S]:
        """Apply a synchronous function with return type
        [`ResultIterable`][trcks.ResultIterable] to the wrapped
        [`Failure`][trcks.Failure] object.

        Wrapped [`SuccessTuple`][trcks.SuccessTuple] objects are passed on unchanged.

        Args:
            callable_: The synchronous function to be applied.
            *args:
                Positional arguments to be passed to `callable_`.
            **kwargs:
                Keyword arguments to be passed to `callable_`.

        Returns:
            A new [`AwaitableResultTupleWrapper`][trcks.oop.AwaitableResultTupleWrapper]
                instance with

                - the result of the function application if
                    the original [`AwaitableResultTuple`][trcks.AwaitableResultTuple] is
                    a failure, or
                - the original [`AwaitableResultTuple`][trcks.AwaitableResultTuple] if
                  it is a success.

        Examples:
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
            ...     .map_failure_to_result_iterable(_recover_from_not_found)
            ... )
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('success', (0,))
            >>>
            >>> wrapper_2 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_failure("fatal")
            ...     .map_failure_to_result_iterable(_recover_from_not_found)
            ... )
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('failure', 'fatal')
            >>>
            >>> wrapper_3 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_successes_from_iterable((1, 2))
            ...     .map_failure_to_result_iterable(_recover_from_not_found)
            ... )
            >>> wrapper_3
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_3.core_as_coroutine)
            ('success', (1, 2))
        """
        return AwaitableResultTupleWrapper(
            art.map_failure_to_result_iterable(callable_, *args, **kwargs)(self.core)
        )

    @deprecated("Use map_failure_to_result_iterable instead")
    def map_failure_to_result_tuple(
        self,
        callable_: Callable[Concatenate[_F_default_co, _P], ResultTuple[_F, _S]],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AwaitableResultTupleWrapper[_F, _S_default_co | _S]:
        """Deprecated alias for
        [`map_failure_to_result_iterable`][trcks.oop.AwaitableResultTupleWrapper.map_failure_to_result_iterable].
        """
        return self.map_failure_to_result_iterable(
            callable_, *args, **kwargs
        )  # pragma: no cover

    @deprecated("Use map_failure_to_iterable instead")
    def map_failure_to_tuple(
        self,
        callable_: Callable[Concatenate[_F_default_co, _P], tuple[_S, ...]],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AwaitableResultTupleWrapper[Never, _S_default_co | _S]:
        """Deprecated alias for
        [`map_failure_to_iterable`][trcks.oop.AwaitableResultTupleWrapper.map_failure_to_iterable].
        """
        return self.map_failure_to_iterable(
            callable_, *args, **kwargs
        )  # pragma: no cover

    def map_successes(
        self,
        callable_: Callable[Concatenate[_S_default_co, _P], _S],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AwaitableResultTupleWrapper[_F_default_co, _S]:
        """Apply a synchronous function to each element in the wrapped
        [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple].

        Wrapped [`Failure`][trcks.Failure] objects are passed on unchanged.

        Args:
            callable_: The synchronous function to be applied to each success element.
            *args:
                Positional arguments to be passed to `callable_`.
            **kwargs:
                Keyword arguments to be passed to `callable_`.

        Returns:
            A new [`AwaitableResultTupleWrapper`][trcks.oop.AwaitableResultTupleWrapper]
                instance with

                - the original [`AwaitableResultTuple`][trcks.AwaitableResultTuple] if
                  it is a failure, or
                - an [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple] with
                  transformed elements if the original
                  [`AwaitableResultTuple`][trcks.AwaitableResultTuple] is a success.

        Examples:
            >>> import asyncio
            >>> from trcks.oop import AwaitableResultTupleWrapper
            >>> wrapper_1 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_successes_from_iterable((1, 2, 3))
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
        return AwaitableResultTupleWrapper(
            art.map_successes(callable_, *args, **kwargs)(self.core)
        )

    def map_successes_to_awaitable(
        self,
        callable_: Callable[Concatenate[_S_default_co, _P], Awaitable[_S]],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AwaitableResultTupleWrapper[_F_default_co, _S]:
        """Apply an asynchronous function to each element in the wrapped
        [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple].

        Wrapped [`Failure`][trcks.Failure] objects are passed on unchanged.

        Args:
            callable_: The asynchronous function to be applied to each success element.
            *args:
                Positional arguments to be passed to `callable_`.
            **kwargs:
                Keyword arguments to be passed to `callable_`.

        Returns:
            A new [`AwaitableResultTupleWrapper`][trcks.oop.AwaitableResultTupleWrapper]
                instance with

                - the original [`AwaitableResultTuple`][trcks.AwaitableResultTuple] if
                  it is a failure, or
                - an [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple] with
                  transformed elements if the original
                  [`AwaitableResultTuple`][trcks.AwaitableResultTuple] is a success.

        Examples:
            >>> import asyncio
            >>> from trcks.oop import AwaitableResultTupleWrapper
            >>> async def _slowly_double_integer(n: int) -> int:
            ...     await asyncio.sleep(0.001)
            ...     return n * 2
            ...
            >>> wrapper_1 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_successes_from_iterable((1, 2, 3))
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
        return AwaitableResultTupleWrapper(
            art.map_successes_to_awaitable(callable_, *args, **kwargs)(self.core)
        )

    def map_successes_to_awaitable_iterable(
        self,
        callable_: Callable[Concatenate[_S_default_co, _P], AwaitableIterable[_S]],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AwaitableResultTupleWrapper[_F_default_co, _S]:
        """Apply an asynchronous function returning an
        [`Iterable`][collections.abc.Iterable] to each element in the wrapped
        [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple] and flatten.

        Wrapped [`Failure`][trcks.Failure] objects are passed on unchanged.

        Args:
            callable_: The asynchronous function returning an
                [`Iterable`][collections.abc.Iterable] to be applied to each success
                element.
            *args:
                Positional arguments to be passed to `callable_`.
            **kwargs:
                Keyword arguments to be passed to `callable_`.

        Returns:
            A new [`AwaitableResultTupleWrapper`][trcks.oop.AwaitableResultTupleWrapper]
                instance with

                - the original [`AwaitableResultTuple`][trcks.AwaitableResultTuple] if
                  it is a failure, or
                - a flattened [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple] if
                    the original [`AwaitableResultTuple`][trcks.AwaitableResultTuple] is
                    a success.

        Examples:
            >>> import asyncio
            >>> from trcks.oop import AwaitableResultTupleWrapper
            >>> async def _slowly_duplicate_integer(n: int) -> tuple[int, int]:
            ...     await asyncio.sleep(0.001)
            ...     return n, n
            ...
            >>> wrapper_1 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_successes_from_iterable([1, 2])
            ...     .map_successes_to_awaitable_iterable(_slowly_duplicate_integer)
            ... )
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('success', (1, 1, 2, 2))
            >>>
            >>> wrapper_2 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_failure("oops")
            ...     .map_successes_to_awaitable_iterable(_slowly_duplicate_integer)
            ... )
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('failure', 'oops')
        """
        return AwaitableResultTupleWrapper(
            art.map_successes_to_awaitable_iterable(callable_, *args, **kwargs)(
                self.core
            )
        )

    def map_successes_to_awaitable_result(
        self,
        callable_: Callable[Concatenate[_S_default_co, _P], AwaitableResult[_F, _S]],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AwaitableResultTupleWrapper[_F_default_co | _F, _S]:
        """Apply an asynchronous function with return type
        [`AwaitableResult`][trcks.AwaitableResult] to each element in the wrapped
        [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple].

        Wrapped [`Failure`][trcks.Failure] objects are passed on unchanged.
        Short-circuits on the first failure returned by the function.

        Args:
            callable_: The asynchronous function to be applied to each success element.
            *args:
                Positional arguments to be passed to `callable_`.
            **kwargs:
                Keyword arguments to be passed to `callable_`.

        Returns:
            A new [`AwaitableResultTupleWrapper`][trcks.oop.AwaitableResultTupleWrapper]
                instance with

                - the original [`AwaitableResultTuple`][trcks.AwaitableResultTuple] if
                  it is a failure,
                - the first [`Failure`][trcks.Failure] returned by the function, or
                - an [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple] with all
                  transformed elements if the function returns success for all elements.

        Examples:
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
            ...     .construct_successes_from_iterable((1, 2))
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
            ...     .construct_successes_from_iterable((1, -1, 2))
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
            art.map_successes_to_awaitable_result(callable_, *args, **kwargs)(self.core)
        )

    def map_successes_to_awaitable_result_iterable(
        self,
        callable_: Callable[
            Concatenate[_S_default_co, _P], AwaitableResultIterable[_F, _S]
        ],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AwaitableResultTupleWrapper[_F_default_co | _F, _S]:
        """Apply an asynchronous function with return type
        [`AwaitableResultIterable`][trcks.AwaitableResultIterable] to each element in
        the wrapped [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple] and flatten.

        Wrapped [`Failure`][trcks.Failure] objects are passed on unchanged.
        Short-circuits on the first failure returned by the function.

        Args:
            callable_: The asynchronous function to be applied to each success element.
            *args:
                Positional arguments to be passed to `callable_`.
            **kwargs:
                Keyword arguments to be passed to `callable_`.

        Returns:
            A new [`AwaitableResultTupleWrapper`][trcks.oop.AwaitableResultTupleWrapper]
                instance with

                - the original [`AwaitableResultTuple`][trcks.AwaitableResultTuple] if
                  it is a failure,
                - the first [`Failure`][trcks.Failure] returned by the function, or
                - a flattened [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple] if
                  the function returns success for all elements.

        Examples:
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
            ...     .construct_successes_from_iterable((1, 2))
            ...     .map_successes_to_awaitable_result_iterable(
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
            ...     .construct_successes_from_iterable((1, -1, 2))
            ...     .map_successes_to_awaitable_result_iterable(
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
            ...     .map_successes_to_awaitable_result_iterable(
            ...         _slowly_duplicate_integer_if_positive
            ...     )
            ... )
            >>> wrapper_3
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_3.core_as_coroutine)
            ('failure', 'oops')
        """
        return AwaitableResultTupleWrapper(
            art.map_successes_to_awaitable_result_iterable(callable_, *args, **kwargs)(
                self.core
            )
        )

    @deprecated("Use map_successes_to_awaitable_result_iterable instead")
    def map_successes_to_awaitable_result_tuple(
        self,
        callable_: Callable[
            Concatenate[_S_default_co, _P], AwaitableResultTuple[_F, _S]
        ],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AwaitableResultTupleWrapper[_F_default_co | _F, _S]:
        """Deprecated alias for
        [`map_successes_to_awaitable_result_iterable`][trcks.oop.AwaitableResultTupleWrapper.map_successes_to_awaitable_result_iterable].
        """
        return self.map_successes_to_awaitable_result_iterable(
            callable_, *args, **kwargs
        )  # pragma: no cover

    @deprecated("Use map_successes_to_awaitable_iterable instead")
    def map_successes_to_awaitable_tuple(
        self,
        callable_: Callable[Concatenate[_S_default_co, _P], AwaitableTuple[_S]],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AwaitableResultTupleWrapper[_F_default_co, _S]:
        """Deprecated alias for
        [`map_successes_to_awaitable_iterable`][trcks.oop.AwaitableResultTupleWrapper.map_successes_to_awaitable_iterable].
        """
        return self.map_successes_to_awaitable_iterable(
            callable_, *args, **kwargs
        )  # pragma: no cover

    def map_successes_to_iterable(
        self,
        callable_: Callable[Concatenate[_S_default_co, _P], Iterable[_S]],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AwaitableResultTupleWrapper[_F_default_co, _S]:
        """Apply a synchronous function returning an
        [`Iterable`][collections.abc.Iterable] to each element in the wrapped
        [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple] and flatten.

        Wrapped [`Failure`][trcks.Failure] objects are passed on unchanged.

        Args:
            callable_: The synchronous function returning an
                [`Iterable`][collections.abc.Iterable] to be applied to each success
                element.
            *args:
                Positional arguments to be passed to `callable_`.
            **kwargs:
                Keyword arguments to be passed to `callable_`.

        Returns:
            A new [`AwaitableResultTupleWrapper`][trcks.oop.AwaitableResultTupleWrapper]
                instance with

                - the original [`AwaitableResultTuple`][trcks.AwaitableResultTuple] if
                  it is a failure, or
                - a flattened [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple] if
                    the original [`AwaitableResultTuple`][trcks.AwaitableResultTuple] is
                    a success.

        Examples:
            >>> import asyncio
            >>> from trcks.oop import AwaitableResultTupleWrapper
            >>> def _duplicate_integer(n: int) -> tuple[int, int]:
            ...     return n, n
            ...
            >>> wrapper_1 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_successes_from_iterable((1, 2))
            ...     .map_successes_to_iterable(_duplicate_integer)
            ... )
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('success', (1, 1, 2, 2))
        """
        return AwaitableResultTupleWrapper(
            art.map_successes_to_iterable(callable_, *args, **kwargs)(self.core)
        )

    def map_successes_to_result(
        self,
        callable_: Callable[Concatenate[_S_default_co, _P], Result[_F, _S]],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AwaitableResultTupleWrapper[_F_default_co | _F, _S]:
        """Apply a synchronous function with return type [`Result`][trcks.Result] to
        each element in the wrapped
        [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple].

        Wrapped [`Failure`][trcks.Failure] objects are passed on unchanged.
        Short-circuits on the first failure returned by the function.

        Args:
            callable_: The synchronous function to be applied to each success element.
            *args:
                Positional arguments to be passed to `callable_`.
            **kwargs:
                Keyword arguments to be passed to `callable_`.

        Returns:
            A new [`AwaitableResultTupleWrapper`][trcks.oop.AwaitableResultTupleWrapper]
                instance with

                - the original [`AwaitableResultTuple`][trcks.AwaitableResultTuple] if
                  it is a failure,
                - the first [`Failure`][trcks.Failure] returned by the function, or
                - an [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple] with all
                  transformed elements if the function returns success for all elements.

        Examples:
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
            ...     .construct_successes_from_iterable((1, 2))
            ...     .map_successes_to_result(_double_integer_if_positive)
            ... )
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('success', (2, 4))
            >>>
            >>> wrapper_2 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_successes_from_iterable((1, -1, 2))
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
        return AwaitableResultTupleWrapper(
            art.map_successes_to_result(callable_, *args, **kwargs)(self.core)
        )

    def map_successes_to_result_iterable(
        self,
        callable_: Callable[Concatenate[_S_default_co, _P], ResultIterable[_F, _S]],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AwaitableResultTupleWrapper[_F_default_co | _F, _S]:
        """Apply a synchronous function with return type
        [`ResultIterable`][trcks.ResultIterable] to each element in the wrapped
        [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple] and flatten.

        Wrapped [`Failure`][trcks.Failure] objects are passed on unchanged.
        Short-circuits on the first failure returned by the function.

        Args:
            callable_: The synchronous function to be applied to each success element.
            *args:
                Positional arguments to be passed to `callable_`.
            **kwargs:
                Keyword arguments to be passed to `callable_`.

        Returns:
            A new [`AwaitableResultTupleWrapper`][trcks.oop.AwaitableResultTupleWrapper]
                instance with

                - the original [`AwaitableResultTuple`][trcks.AwaitableResultTuple] if
                  it is a failure,
                - the first [`Failure`][trcks.Failure] returned by the function, or
                - a flattened [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple] if
                  the function returns success for all elements.

        Examples:
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
            ...     .construct_successes_from_iterable((1, 2))
            ...     .map_successes_to_result_iterable(_duplicate_integer_if_positive)
            ... )
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('success', (1, 1, 2, 2))
            >>>
            >>> wrapper_2 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_failure("oops")
            ...     .map_successes_to_result_iterable(_duplicate_integer_if_positive)
            ... )
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('failure', 'oops')
        """
        return AwaitableResultTupleWrapper(
            art.map_successes_to_result_iterable(callable_, *args, **kwargs)(self.core)
        )

    @deprecated("Use map_successes_to_result_iterable instead")
    def map_successes_to_result_tuple(
        self,
        callable_: Callable[Concatenate[_S_default_co, _P], ResultTuple[_F, _S]],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AwaitableResultTupleWrapper[_F_default_co | _F, _S]:
        """Deprecated alias for
        [`map_successes_to_result_iterable`][trcks.oop.AwaitableResultTupleWrapper.map_successes_to_result_iterable].
        """
        return self.map_successes_to_result_iterable(
            callable_, *args, **kwargs
        )  # pragma: no cover

    @deprecated("Use map_successes_to_iterable instead")
    def map_successes_to_tuple(
        self,
        callable_: Callable[Concatenate[_S_default_co, _P], tuple[_S, ...]],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AwaitableResultTupleWrapper[_F_default_co, _S]:
        """Deprecated alias for
        [`map_successes_to_iterable`][trcks.oop.AwaitableResultTupleWrapper.map_successes_to_iterable].
        """
        return self.map_successes_to_iterable(
            callable_, *args, **kwargs
        )  # pragma: no cover

    def tap_failure(
        self,
        callable_: Callable[Concatenate[_F_default_co, _P], object],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AwaitableResultTupleWrapper[_F_default_co, _S_default_co]:
        """Apply a synchronous side effect to the wrapped [`Failure`][trcks.Failure]
        object.

        Wrapped [`SuccessTuple`][trcks.SuccessTuple] objects are passed on without side
        effects.

        Args:
            callable_: The synchronous side effect to be applied.
            *args:
                Positional arguments to be passed to `callable_`.
            **kwargs:
                Keyword arguments to be passed to `callable_`.

        Returns:
            A new [`AwaitableResultTupleWrapper`][trcks.oop.AwaitableResultTupleWrapper]
                instance
                with the original [`AwaitableResultTuple`][trcks.AwaitableResultTuple]
                object, allowing for further method chaining.

        Examples:
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
            >>> wrapper_2 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_successes_from_iterable((1,))
            ...     .tap_failure(_log_failure))
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> result_2 = asyncio.run(wrapper_2.core_as_coroutine)
            >>> result_2
            ('success', (1,))
        """
        return AwaitableResultTupleWrapper(
            art.tap_failure(callable_, *args, **kwargs)(self.core)
        )

    def tap_failure_to_awaitable(
        self,
        callable_: Callable[Concatenate[_F_default_co, _P], Awaitable[object]],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AwaitableResultTupleWrapper[_F_default_co, _S_default_co]:
        """Apply an asynchronous side effect to the wrapped [`Failure`][trcks.Failure]
        object.

        Wrapped [`SuccessTuple`][trcks.SuccessTuple] objects are passed on without side
        effects.

        Args:
            callable_: The asynchronous side effect to be applied.
            *args:
                Positional arguments to be passed to `callable_`.
            **kwargs:
                Keyword arguments to be passed to `callable_`.

        Returns:
            A new [`AwaitableResultTupleWrapper`][trcks.oop.AwaitableResultTupleWrapper]
                instance
                with the original [`AwaitableResultTuple`][trcks.AwaitableResultTuple]
                object, allowing for further method chaining.

        Examples:
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
            >>> wrapper_2 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_successes_from_iterable((1,))
            ...     .tap_failure_to_awaitable(_slowly_log_failure))
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> result_2 = asyncio.run(wrapper_2.core_as_coroutine)
            >>> result_2
            ('success', (1,))
        """
        return AwaitableResultTupleWrapper(
            art.tap_failure_to_awaitable(callable_, *args, **kwargs)(self.core)
        )

    def tap_failure_to_awaitable_iterable(
        self,
        callable_: Callable[Concatenate[_F_default_co, _P], AwaitableIterable[object]],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AwaitableResultTupleWrapper[Never, _F_default_co | _S_default_co]:
        """Apply an asynchronous side effect returning an
        [`Iterable`][collections.abc.Iterable] to the wrapped [`Failure`][trcks.Failure]
        object.

        The failure is converted to an
        [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple] where the original
        failure value is repeated once per element in the
        [`Iterable`][collections.abc.Iterable] returned by the side effect.

        Wrapped [`SuccessTuple`][trcks.SuccessTuple] objects are passed on without side
        effects.

        Args:
            callable_: The asynchronous side effect returning an
                [`Iterable`][collections.abc.Iterable] to be applied.
            *args:
                Positional arguments to be passed to `callable_`.
            **kwargs:
                Keyword arguments to be passed to `callable_`.

        Returns:
            A new [`AwaitableResultTupleWrapper`][trcks.oop.AwaitableResultTupleWrapper]
                instance with

                - an [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple] containing
                  the original failure repeated once per element in the tuple returned
                  by the side effect if the original
                  [`AwaitableResultTuple`][trcks.AwaitableResultTuple] is a failure, or
                - the original [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple]
                    if no side effect was applied.

        Examples:
            >>> import asyncio
            >>> from trcks.oop import AwaitableResultTupleWrapper
            >>> async def _slowly_log_and_alert(
            ...     description: str,
            ... ) -> tuple[None, None]:
            ...     await asyncio.sleep(0.001)
            ...     return (
            ...         print(f"Failure: {description}"),
            ...         print(f"Logged: {description}"),
            ...     )
            ...
            >>> wrapper_1 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_failure("critical")
            ...     .tap_failure_to_awaitable_iterable(_slowly_log_and_alert)
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
            ...     .construct_successes_from_iterable((1,))
            ...     .tap_failure_to_awaitable_iterable(_slowly_log_and_alert)
            ... )
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('success', (1,))
        """
        tapped_callable: Callable[
            [AwaitableResultTuple[_F_default_co, _S_default_co]],
            AwaitableResultTuple[Never, _F_default_co | _S_default_co],
        ] = art.tap_failure_to_awaitable_iterable(callable_, *args, **kwargs)
        return AwaitableResultTupleWrapper(tapped_callable(self.core))

    def tap_failure_to_awaitable_result(
        self,
        callable_: Callable[
            Concatenate[_F_default_co, _P], AwaitableResult[object, _S]
        ],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AwaitableResultTupleWrapper[_F_default_co, _S_default_co | _S]:
        """Apply an asynchronous side effect with return type
        [`AwaitableResult`][trcks.AwaitableResult] to the wrapped
        [`Failure`][trcks.Failure] object.

        Wrapped [`SuccessTuple`][trcks.SuccessTuple] objects are passed on without side
        effects.

        Args:
            callable_: The asynchronous side effect to be applied.
            *args:
                Positional arguments to be passed to `callable_`.
            **kwargs:
                Keyword arguments to be passed to `callable_`.

        Returns:
            A new [`AwaitableResultTupleWrapper`][trcks.oop.AwaitableResultTupleWrapper]
                instance with

                - *the original* [`Failure`][trcks.Failure]
                    if the applied side effect returns a [`Failure`][trcks.Failure],
                - *the returned* [`Success`][trcks.Success] (wrapped as a tuple)
                    if the applied side effect returns a [`Success`][trcks.Success] and
                - *the original* [`SuccessTuple`][trcks.SuccessTuple]
                    if no side effect was applied.

        Examples:
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
            art.tap_failure_to_awaitable_result(callable_, *args, **kwargs)(self.core)
        )

    def tap_failure_to_awaitable_result_iterable(
        self,
        callable_: Callable[
            Concatenate[_F_default_co, _P], AwaitableResultIterable[object, _S]
        ],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AwaitableResultTupleWrapper[_F_default_co, _S_default_co | _S]:
        """Apply an asynchronous side effect with return type
        [`AwaitableResultIterable`][trcks.AwaitableResultIterable] to the wrapped
        [`Failure`][trcks.Failure] object.

        Wrapped [`SuccessTuple`][trcks.SuccessTuple] objects are passed on without side
        effects.

        Args:
            callable_: The asynchronous side effect to be applied.
            *args:
                Positional arguments to be passed to `callable_`.
            **kwargs:
                Keyword arguments to be passed to `callable_`.

        Returns:
            A new [`AwaitableResultTupleWrapper`][trcks.oop.AwaitableResultTupleWrapper]
                instance with

                - *the original* [`Failure`][trcks.Failure]
                    if the applied side effect returns a [`Failure`][trcks.Failure],
                - *the returned* [`SuccessTuple`][trcks.SuccessTuple]
                    if the applied side effect returns a
                    [`SuccessTuple`][trcks.SuccessTuple] and
                - *the original* [`SuccessTuple`][trcks.SuccessTuple]
                    if no side effect was applied.

        Examples:
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
            ...     .tap_failure_to_awaitable_result_iterable(
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
            ...     .tap_failure_to_awaitable_result_iterable(
            ...         _slowly_recover_from_not_found,
            ...     )
            ... )
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('failure', 'fatal')
        """
        return AwaitableResultTupleWrapper(
            art.tap_failure_to_awaitable_result_iterable(callable_, *args, **kwargs)(
                self.core
            )
        )

    @deprecated("Use tap_failure_to_awaitable_result_iterable instead")
    def tap_failure_to_awaitable_result_tuple(
        self,
        callable_: Callable[
            Concatenate[_F_default_co, _P], AwaitableResultTuple[object, _S]
        ],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AwaitableResultTupleWrapper[_F_default_co, _S_default_co | _S]:
        """Deprecated alias for
        [`tap_failure_to_awaitable_result_iterable`][trcks.oop.AwaitableResultTupleWrapper.tap_failure_to_awaitable_result_iterable].
        """
        return self.tap_failure_to_awaitable_result_iterable(
            callable_, *args, **kwargs
        )  # pragma: no cover

    @deprecated("Use tap_failure_to_awaitable_iterable instead")
    def tap_failure_to_awaitable_tuple(
        self,
        callable_: Callable[Concatenate[_F_default_co, _P], AwaitableTuple[object]],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AwaitableResultTupleWrapper[Never, _F_default_co | _S_default_co]:
        """Deprecated alias for
        [`tap_failure_to_awaitable_iterable`][trcks.oop.AwaitableResultTupleWrapper.tap_failure_to_awaitable_iterable].
        """
        return self.tap_failure_to_awaitable_iterable(
            callable_, *args, **kwargs
        )  # pragma: no cover

    def tap_failure_to_iterable(
        self,
        callable_: Callable[Concatenate[_F_default_co, _P], Iterable[object]],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AwaitableResultTupleWrapper[Never, _F_default_co | _S_default_co]:
        """Apply a synchronous side effect returning an
        [`Iterable`][collections.abc.Iterable] to the wrapped [`Failure`][trcks.Failure]
        object.

        The failure is converted to an
        [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple] where the original
        failure value is repeated once per element in the
        [`Iterable`][collections.abc.Iterable] returned by the side effect.

        Wrapped [`SuccessTuple`][trcks.SuccessTuple] objects are passed on without side
        effects.

        Args:
            callable_: The synchronous side effect returning an
                [`Iterable`][collections.abc.Iterable] to be applied.
            *args:
                Positional arguments to be passed to `callable_`.
            **kwargs:
                Keyword arguments to be passed to `callable_`.

        Returns:
            A new [`AwaitableResultTupleWrapper`][trcks.oop.AwaitableResultTupleWrapper]
                instance with

                - an [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple] containing
                  the original failure repeated once per element in the tuple returned
                  by the side effect if the original
                  [`AwaitableResultTuple`][trcks.AwaitableResultTuple] is a failure, or
                - the original [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple]
                    if no side effect was applied.

        Examples:
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
            ...     .tap_failure_to_iterable(_log_and_alert)
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
            ...     .construct_successes_from_iterable((1,))
            ...     .tap_failure_to_iterable(_log_and_alert)
            ... )
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('success', (1,))
        """
        tapped_callable: Callable[
            [AwaitableResultTuple[_F_default_co, _S_default_co]],
            AwaitableResultTuple[Never, _F_default_co | _S_default_co],
        ] = art.tap_failure_to_iterable(callable_, *args, **kwargs)
        return AwaitableResultTupleWrapper(tapped_callable(self.core))

    def tap_failure_to_result(
        self,
        callable_: Callable[Concatenate[_F_default_co, _P], Result[object, _S]],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AwaitableResultTupleWrapper[_F_default_co, _S_default_co | _S]:
        """Apply a synchronous side effect with return type [`Result`][trcks.Result]
        to the wrapped [`Failure`][trcks.Failure] object.

        Wrapped [`SuccessTuple`][trcks.SuccessTuple] objects are passed on without side
        effects.

        Args:
            callable_: The synchronous side effect to be applied.
            *args:
                Positional arguments to be passed to `callable_`.
            **kwargs:
                Keyword arguments to be passed to `callable_`.

        Returns:
            A new [`AwaitableResultTupleWrapper`][trcks.oop.AwaitableResultTupleWrapper]
                instance with

                - *the original* [`Failure`][trcks.Failure]
                    if the applied side effect returns a [`Failure`][trcks.Failure],
                - *the returned* [`Success`][trcks.Success] (wrapped as a tuple)
                    if the applied side effect returns a [`Success`][trcks.Success] and
                - *the original* [`SuccessTuple`][trcks.SuccessTuple]
                    if no side effect was applied.

        Examples:
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
            ...     .construct_successes_from_iterable((1,))
            ...     .tap_failure_to_result(_recover_from_not_found)
            ... )
            >>> wrapper_3
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_3.core_as_coroutine)
            ('success', (1,))
        """
        return AwaitableResultTupleWrapper(
            art.tap_failure_to_result(callable_, *args, **kwargs)(self.core)
        )

    def tap_failure_to_result_iterable(
        self,
        callable_: Callable[Concatenate[_F_default_co, _P], ResultIterable[object, _S]],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AwaitableResultTupleWrapper[_F_default_co, _S_default_co | _S]:
        """Apply a synchronous side effect with return type
        [`ResultIterable`][trcks.ResultIterable] to the wrapped
        [`Failure`][trcks.Failure] object.

        Wrapped [`SuccessTuple`][trcks.SuccessTuple] objects are passed on without side
        effects.

        Args:
            callable_: The synchronous side effect to be applied.
            *args:
                Positional arguments to be passed to `callable_`.
            **kwargs:
                Keyword arguments to be passed to `callable_`.

        Returns:
            A new [`AwaitableResultTupleWrapper`][trcks.oop.AwaitableResultTupleWrapper]
                instance with

                - *the original* [`Failure`][trcks.Failure]
                    if the applied side effect returns a [`Failure`][trcks.Failure],
                - *the returned* [`SuccessIterable`][trcks.SuccessIterable]
                    if the applied side effect returns a
                    [`SuccessIterable`][trcks.SuccessIterable] and
                - *the original* [`SuccessTuple`][trcks.SuccessTuple]
                    if no side effect was applied.

        Examples:
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
            ...     .tap_failure_to_result_iterable(_recover_from_not_found)
            ... )
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('success', (0,))
            >>>
            >>> wrapper_2 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_failure("fatal")
            ...     .tap_failure_to_result_iterable(_recover_from_not_found)
            ... )
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('failure', 'fatal')
            >>>
            >>> wrapper_3 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_successes_from_iterable((1,))
            ...     .tap_failure_to_result_iterable(_recover_from_not_found)
            ... )
            >>> wrapper_3
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_3.core_as_coroutine)
            ('success', (1,))
        """
        return AwaitableResultTupleWrapper(
            art.tap_failure_to_result_iterable(callable_, *args, **kwargs)(self.core)
        )

    @deprecated("Use tap_failure_to_result_iterable instead")
    def tap_failure_to_result_tuple(
        self,
        callable_: Callable[Concatenate[_F_default_co, _P], ResultTuple[object, _S]],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AwaitableResultTupleWrapper[_F_default_co, _S_default_co | _S]:
        """Deprecated alias for
        [`tap_failure_to_result_iterable`][trcks.oop.AwaitableResultTupleWrapper.tap_failure_to_result_iterable].
        """
        return self.tap_failure_to_result_iterable(
            callable_, *args, **kwargs
        )  # pragma: no cover

    @deprecated("Use tap_failure_to_iterable instead")
    def tap_failure_to_tuple(
        self,
        callable_: Callable[Concatenate[_F_default_co, _P], tuple[object, ...]],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AwaitableResultTupleWrapper[Never, _F_default_co | _S_default_co]:
        """Deprecated alias for
        [`tap_failure_to_iterable`][trcks.oop.AwaitableResultTupleWrapper.tap_failure_to_iterable].
        """
        return self.tap_failure_to_iterable(
            callable_, *args, **kwargs
        )  # pragma: no cover

    def tap_successes(
        self,
        callable_: Callable[Concatenate[_S_default_co, _P], object],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AwaitableResultTupleWrapper[_F_default_co, _S_default_co]:
        """Apply a synchronous side effect to each element in the wrapped
        [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple].

        Wrapped [`Failure`][trcks.Failure] objects are passed on without side effects.

        Args:
            callable_: The synchronous side effect to be
                applied to each success element.
            *args:
                Positional arguments to be passed to `callable_`.
            **kwargs:
                Keyword arguments to be passed to `callable_`.

        Returns:
            A new [`AwaitableResultTupleWrapper`][trcks.oop.AwaitableResultTupleWrapper]
                instance
                with the original [`AwaitableResultTuple`][trcks.AwaitableResultTuple]
                object, allowing for further method chaining.

        Examples:
            >>> import asyncio
            >>> from trcks.oop import AwaitableResultTupleWrapper
            >>> def _log_value(n: int) -> None:
            ...     print(f"Value: {n}")
            ...
            >>> wrapper_1 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_successes_from_iterable((1, 2))
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
        return AwaitableResultTupleWrapper(
            art.tap_successes(callable_, *args, **kwargs)(self.core)
        )

    def tap_successes_to_awaitable(
        self,
        callable_: Callable[Concatenate[_S_default_co, _P], Awaitable[object]],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AwaitableResultTupleWrapper[_F_default_co, _S_default_co]:
        """Apply an asynchronous side effect to each element in the wrapped
        [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple].

        Wrapped [`Failure`][trcks.Failure] objects are passed on without side effects.

        Args:
            callable_: The asynchronous side effect to be
                applied to each success element.
            *args:
                Positional arguments to be passed to `callable_`.
            **kwargs:
                Keyword arguments to be passed to `callable_`.

        Returns:
            A new [`AwaitableResultTupleWrapper`][trcks.oop.AwaitableResultTupleWrapper]
                instance
                with the original [`AwaitableResultTuple`][trcks.AwaitableResultTuple]
                object, allowing for further method chaining.

        Examples:
            >>> import asyncio
            >>> from trcks.oop import AwaitableResultTupleWrapper
            >>> async def _slowly_log_value(n: int) -> None:
            ...     await asyncio.sleep(0.001)
            ...     print(f"Value: {n}")
            ...
            >>> wrapper_1 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_successes_from_iterable((1, 2))
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
        return AwaitableResultTupleWrapper(
            art.tap_successes_to_awaitable(callable_, *args, **kwargs)(self.core)
        )

    def tap_successes_to_awaitable_iterable(
        self,
        callable_: Callable[Concatenate[_S_default_co, _P], AwaitableIterable[object]],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AwaitableResultTupleWrapper[_F_default_co, _S_default_co]:
        """Apply an asynchronous side effect returning an
        [`Iterable`][collections.abc.Iterable] to each element in the wrapped
        [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple].

        The number of side effect outputs determines how many times each
        original element is repeated in the resulting tuple.

        Wrapped [`Failure`][trcks.Failure] objects are passed on without side effects.

        Args:
            callable_: The asynchronous side effect returning an
                [`Iterable`][collections.abc.Iterable] to be applied to each success
                element.
            *args:
                Positional arguments to be passed to `callable_`.
            **kwargs:
                Keyword arguments to be passed to `callable_`.

        Returns:
            A new [`AwaitableResultTupleWrapper`][trcks.oop.AwaitableResultTupleWrapper]
                instance with

                - the original [`AwaitableResultTuple`][trcks.AwaitableResultTuple] if
                  it is a failure, or
                - an [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple] where each
                  original success element is repeated once per element returned by the
                  side effect.

        Examples:
            >>> import asyncio
            >>> from trcks.oop import AwaitableResultTupleWrapper
            >>> async def _slowly_log_twice(n: int) -> tuple[None, None]:
            ...     await asyncio.sleep(0.001)
            ...     return print(f"Received: {n}"), print(f"Received: {n}")
            ...
            >>> wrapper = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_successes_from_iterable([7])
            ...     .tap_successes_to_awaitable_iterable(_slowly_log_twice)
            ... )
            >>> wrapper
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> result = asyncio.run(wrapper.core_as_coroutine)
            Received: 7
            Received: 7
            >>> result
            ('success', (7, 7))
        """
        return AwaitableResultTupleWrapper(
            art.tap_successes_to_awaitable_iterable(callable_, *args, **kwargs)(
                self.core
            )
        )

    def tap_successes_to_awaitable_result(
        self,
        callable_: Callable[
            Concatenate[_S_default_co, _P], AwaitableResult[_F, object]
        ],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AwaitableResultTupleWrapper[_F_default_co | _F, _S_default_co]:
        """Apply an asynchronous side effect with return type
        [`AwaitableResult`][trcks.AwaitableResult] to each element in the wrapped
        [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple].

        Wrapped [`Failure`][trcks.Failure] objects are passed on without side effects.

        Args:
            callable_: The asynchronous side effect to be
                applied to each success element.
            *args:
                Positional arguments to be passed to `callable_`.
            **kwargs:
                Keyword arguments to be passed to `callable_`.

        Returns:
            A new [`AwaitableResultTupleWrapper`][trcks.oop.AwaitableResultTupleWrapper]
                instance with

                - *the original* [`Failure`][trcks.Failure] if no side effect was
                  applied,
                - *the returned* [`Failure`][trcks.Failure]
                    if the applied side effect returns a [`Failure`][trcks.Failure] and
                - *the original* [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple]
                    if the applied side effect returns success for all elements.

        Examples:
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
            ...     .construct_successes_from_iterable((1, 2))
            ...     .tap_successes_to_awaitable_result(_validate_positive)
            ... )
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('success', (1, 2))
            >>>
            >>> wrapper_2 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_successes_from_iterable((1, -1))
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
            art.tap_successes_to_awaitable_result(callable_, *args, **kwargs)(self.core)
        )

    def tap_successes_to_awaitable_result_iterable(
        self,
        callable_: Callable[
            Concatenate[_S_default_co, _P], AwaitableResultIterable[_F, object]
        ],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AwaitableResultTupleWrapper[_F_default_co | _F, _S_default_co]:
        """Apply an asynchronous side effect with return type
        [`AwaitableResultIterable`][trcks.AwaitableResultIterable] to each element in
        the wrapped [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple].

        Wrapped [`Failure`][trcks.Failure] objects are passed on without side effects.

        Args:
            callable_: The asynchronous side effect to be
                applied to each success element.
            *args:
                Positional arguments to be passed to `callable_`.
            **kwargs:
                Keyword arguments to be passed to `callable_`.

        Returns:
            A new [`AwaitableResultTupleWrapper`][trcks.oop.AwaitableResultTupleWrapper]
                instance with

                - *the original* [`Failure`][trcks.Failure] if no side effect was
                  applied,
                - *the returned* [`Failure`][trcks.Failure]
                    if the applied side effect returns a [`Failure`][trcks.Failure] and
                - *the original* success element repeated once per element
                    in the side effect output if the applied side effect returns
                    success for all elements.

        Examples:
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
            ...     .construct_successes_from_iterable((7,))
            ...     .tap_successes_to_awaitable_result_iterable(_validate_positive)
            ... )
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('success', (7, 7))
            >>>
            >>> wrapper_2 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_successes_from_iterable((1, -1))
            ...     .tap_successes_to_awaitable_result_iterable(_validate_positive)
            ... )
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('failure', 'negative')
            >>>
            >>> wrapper_3 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_failure("oops")
            ...     .tap_successes_to_awaitable_result_iterable(_validate_positive)
            ... )
            >>> wrapper_3
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_3.core_as_coroutine)
            ('failure', 'oops')
        """
        return AwaitableResultTupleWrapper(
            art.tap_successes_to_awaitable_result_iterable(callable_, *args, **kwargs)(
                self.core
            )
        )

    @deprecated("Use tap_successes_to_awaitable_result_iterable instead")
    def tap_successes_to_awaitable_result_tuple(
        self,
        callable_: Callable[
            Concatenate[_S_default_co, _P], AwaitableResultTuple[_F, object]
        ],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AwaitableResultTupleWrapper[_F_default_co | _F, _S_default_co]:
        """Deprecated alias for
        [`tap_successes_to_awaitable_result_iterable`][trcks.oop.AwaitableResultTupleWrapper.tap_successes_to_awaitable_result_iterable].
        """
        return self.tap_successes_to_awaitable_result_iterable(
            callable_, *args, **kwargs
        )  # pragma: no cover

    @deprecated("Use tap_successes_to_awaitable_iterable instead")
    def tap_successes_to_awaitable_tuple(
        self,
        callable_: Callable[Concatenate[_S_default_co, _P], AwaitableTuple[object]],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AwaitableResultTupleWrapper[_F_default_co, _S_default_co]:
        """Deprecated alias for
        [`tap_successes_to_awaitable_iterable`][trcks.oop.AwaitableResultTupleWrapper.tap_successes_to_awaitable_iterable].
        """
        return self.tap_successes_to_awaitable_iterable(
            callable_, *args, **kwargs
        )  # pragma: no cover

    def tap_successes_to_iterable(
        self,
        callable_: Callable[Concatenate[_S_default_co, _P], Iterable[object]],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AwaitableResultTupleWrapper[_F_default_co, _S_default_co]:
        """Apply a synchronous side effect returning an
        [`Iterable`][collections.abc.Iterable] to each element in the wrapped
        [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple].

        The original success elements are repeated once per element in the
        [`Iterable`][collections.abc.Iterable] returned by the side effect.

        Wrapped [`Failure`][trcks.Failure] objects are passed on without side effects.

        Args:
            callable_: The synchronous side effect returning an
                [`Iterable`][collections.abc.Iterable] to be applied
                to each success element.
            *args:
                Positional arguments to be passed to `callable_`.
            **kwargs:
                Keyword arguments to be passed to `callable_`.

        Returns:
            A new [`AwaitableResultTupleWrapper`][trcks.oop.AwaitableResultTupleWrapper]
                instance with

                - the original [`Failure`][trcks.Failure] if no side effect was applied,
                  or
                - an [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple] where each
                  original element is repeated once per element in the tuple returned by
                  the side effect.

        Examples:
            >>> import asyncio
            >>> from trcks.oop import AwaitableResultTupleWrapper
            >>> def _log_twice(n: int) -> tuple[None, None]:
            ...     return print(f"Received: {n}"), print(f"Received: {n}")
            ...
            >>> wrapper_1 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_successes_from_iterable((7,))
            ...     .tap_successes_to_iterable(_log_twice)
            ... )
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> result_1 = asyncio.run(wrapper_1.core_as_coroutine)
            Received: 7
            Received: 7
            >>> result_1
            ('success', (7, 7))
        """
        return AwaitableResultTupleWrapper(
            art.tap_successes_to_iterable(callable_, *args, **kwargs)(self.core)
        )

    def tap_successes_to_result(
        self,
        callable_: Callable[Concatenate[_S_default_co, _P], Result[_F, object]],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AwaitableResultTupleWrapper[_F_default_co | _F, _S_default_co]:
        """Apply a synchronous side effect with return type [`Result`][trcks.Result] to
        each element in the wrapped
        [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple].

        Wrapped [`Failure`][trcks.Failure] objects are passed on without side effects.

        Args:
            callable_: The synchronous side effect to be
                applied to each success element.
            *args:
                Positional arguments to be passed to `callable_`.
            **kwargs:
                Keyword arguments to be passed to `callable_`.

        Returns:
            A new [`AwaitableResultTupleWrapper`][trcks.oop.AwaitableResultTupleWrapper]
                instance with

                - *the original* [`Failure`][trcks.Failure] if no side effect was
                  applied,
                - *the returned* [`Failure`][trcks.Failure]
                    if the applied side effect returns a [`Failure`][trcks.Failure] and
                - *the original* [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple]
                    if the applied side effect returns success for all elements.

        Examples:
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
            ...     .construct_successes_from_iterable((1, 2))
            ...     .tap_successes_to_result(_validate_positive)
            ... )
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('success', (1, 2))
            >>>
            >>> wrapper_2 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_successes_from_iterable((1, -1))
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
        return AwaitableResultTupleWrapper(
            art.tap_successes_to_result(callable_, *args, **kwargs)(self.core)
        )

    def tap_successes_to_result_iterable(
        self,
        callable_: Callable[Concatenate[_S_default_co, _P], ResultIterable[_F, object]],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AwaitableResultTupleWrapper[_F_default_co | _F, _S_default_co]:
        """Apply a synchronous side effect with return type
        [`ResultIterable`][trcks.ResultIterable] to each element in the wrapped
        [`AwaitableSuccessTuple`][trcks.AwaitableSuccessTuple].

        Wrapped [`Failure`][trcks.Failure] objects are passed on without side effects.

        Args:
            callable_: The synchronous side effect to be
                applied to each success element.
            *args:
                Positional arguments to be passed to `callable_`.
            **kwargs:
                Keyword arguments to be passed to `callable_`.

        Returns:
            A new [`AwaitableResultTupleWrapper`][trcks.oop.AwaitableResultTupleWrapper]
                instance with

                - *the original* [`Failure`][trcks.Failure] if no side effect was
                  applied,
                - *the returned* [`Failure`][trcks.Failure]
                    if the applied side effect returns a [`Failure`][trcks.Failure] and
                - *the original* success element repeated once per element
                    in the side effect output if the applied side effect returns
                    success for all elements.

        Examples:
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
            ...     .construct_successes_from_iterable((7,))
            ...     .tap_successes_to_result_iterable(_validate_positive_twice)
            ... )
            >>> wrapper_1
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_1.core_as_coroutine)
            ('success', (7, 7))
            >>>
            >>> wrapper_2 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_successes_from_iterable((1, -1))
            ...     .tap_successes_to_result_iterable(_validate_positive_twice)
            ... )
            >>> wrapper_2
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_2.core_as_coroutine)
            ('failure', 'negative')
            >>>
            >>> wrapper_3 = (
            ...     AwaitableResultTupleWrapper
            ...     .construct_failure("oops")
            ...     .tap_successes_to_result_iterable(_validate_positive_twice)
            ... )
            >>> wrapper_3
            AwaitableResultTupleWrapper(core=<coroutine object ...>)
            >>> asyncio.run(wrapper_3.core_as_coroutine)
            ('failure', 'oops')
        """
        return AwaitableResultTupleWrapper(
            art.tap_successes_to_result_iterable(callable_, *args, **kwargs)(self.core)
        )

    @deprecated("Use tap_successes_to_result_iterable instead")
    def tap_successes_to_result_tuple(
        self,
        callable_: Callable[Concatenate[_S_default_co, _P], ResultTuple[_F, object]],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AwaitableResultTupleWrapper[_F_default_co | _F, _S_default_co]:
        """Deprecated alias for
        [`tap_successes_to_result_iterable`][trcks.oop.AwaitableResultTupleWrapper.tap_successes_to_result_iterable].
        """
        return self.tap_successes_to_result_iterable(
            callable_, *args, **kwargs
        )  # pragma: no cover

    @deprecated("Use tap_successes_to_iterable instead")
    def tap_successes_to_tuple(
        self,
        callable_: Callable[Concatenate[_S_default_co, _P], tuple[object, ...]],
        /,
        *args: _P.args,
        **kwargs: _P.kwargs,
    ) -> AwaitableResultTupleWrapper[_F_default_co, _S_default_co]:
        """Deprecated alias for
        [`tap_successes_to_iterable`][trcks.oop.AwaitableResultTupleWrapper.tap_successes_to_iterable].
        """
        return self.tap_successes_to_iterable(
            callable_, *args, **kwargs
        )  # pragma: no cover
