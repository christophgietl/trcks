from __future__ import annotations

from typing import TYPE_CHECKING, final

from trcks import ResultTuple
from trcks._typing import Never, TypeVar, deprecated
from trcks.fp.monads import awaitable_result_tuple as art
from trcks.oop._base_awaitable_wrapper import BaseAwaitableWrapper

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


@final
class AwaitableResultTupleWrapper(
    BaseAwaitableWrapper[ResultTuple[_F_default_co, _S_default_co]]
):
    """Type-safe and immutable wrapper for [trcks.AwaitableResultTuple][] objects.

    The wrapped object can be accessed
    via the attribute [trcks.oop.BaseWrapper.core][].
    The `trcks.oop.AwaitableResultTupleWrapper.map*` methods allow method chaining.
    The `trcks.oop.AwaitableResultTupleWrapper.tap*` methods allow for side effects
    without changing the wrapped [trcks.ResultTuple][].

    Example:
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

    __slots__: tuple[str, ...] = ()

    @staticmethod
    def construct_failure(value: _F) -> AwaitableResultTupleWrapper[_F, Never]:
        """Construct and wrap an awaitable [trcks.Failure][] object from a value.

        Args:
            value: The value to be wrapped.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with
                the wrapped [trcks.AwaitableResultTuple][] object.

        Example:
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
    ) -> AwaitableResultTupleWrapper[_F, Never]:
        """Construct and wrap an awaitable [trcks.Failure][] from an awaitable value.

        Args:
            awtbl: The awaitable value to be wrapped.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with
                the wrapped [trcks.AwaitableResultTuple][] object.

        Example:
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
    ) -> AwaitableResultTupleWrapper[_F, _S]:
        """Construct and wrap an [trcks.AwaitableResultTuple][] from an
        [trcks.AwaitableResult][].

        The success payload is wrapped in a single-element tuple.

        Args:
            a_rslt: The [trcks.AwaitableResult][] object to be converted.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance where
                the success payload is wrapped in a single-element tuple,
                or the original failure is preserved.

        Example:
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
    def construct_from_result(
        rslt: Result[_F_default, _S_default],
    ) -> AwaitableResultTupleWrapper[_F_default, _S_default]:
        """Construct and wrap an [trcks.AwaitableResultTuple][] from a
        [trcks.Result][].

        The success payload is wrapped in a single-element tuple.

        Args:
            rslt: The [trcks.Result][] object to be converted.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance where
                the success payload is wrapped in a single-element tuple,
                or the original failure is preserved.

        Example:
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
    ) -> AwaitableResultTupleWrapper[_F_default, _S_default]:
        """Wrap a [trcks.ResultIterable][] object and convert it into an
        [trcks.AwaitableResultTuple][].

        Args:
            it: The [trcks.ResultIterable][] object to be wrapped and converted.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with
                the wrapped [trcks.AwaitableResultTuple][] object.

        Example:
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
    @deprecated("Use construct_from_result_iterable or the default constructor instead")
    def construct_from_result_tuple(
        cls,
        r_tpl: ResultTuple[_F_default, _S_default],
    ) -> AwaitableResultTupleWrapper[_F_default, _S_default]:
        """Deprecated alias for construct_from_result_iterable."""
        return cls.construct_from_result_iterable(r_tpl)  # pragma: no cover

    @staticmethod
    def construct_successes(value: _S) -> AwaitableResultTupleWrapper[Never, _S]:
        """Construct and wrap an awaitable [trcks.SuccessTuple][] from a value.

        Args:
            value: The value to be wrapped in a single-element tuple.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with
                the wrapped [trcks.AwaitableResultTuple][] object.

        Example:
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
    ) -> AwaitableResultTupleWrapper[Never, _S]:
        """Construct and wrap an awaitable [trcks.SuccessTuple][] from an
        awaitable value.

        Args:
            awtbl: The awaitable value to be wrapped in a single-element tuple.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with
                the wrapped [trcks.AwaitableResultTuple][] object.

        Example:
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
    def construct_successes_from_iterable(
        it: Iterable[_S],
    ) -> AwaitableResultTupleWrapper[Never, _S]:
        """Construct and wrap an awaitable [trcks.SuccessTuple][] from an iterable.

        Args:
            it: The [collections.abc.Iterable][] to be wrapped and converted.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with
                the wrapped [trcks.AwaitableResultTuple][] object.

        Example:
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
    @deprecated(
        "Use construct_successes_from_iterable or the default constructor instead"
    )
    def construct_successes_from_tuple(
        cls,
        tpl: tuple[_S, ...],
    ) -> AwaitableResultTupleWrapper[Never, _S]:
        """Deprecated alias for construct_successes_from_iterable."""
        return cls.construct_successes_from_iterable(tpl)  # pragma: no cover

    def map_failure(
        self, f: Callable[[_F_default_co], _F]
    ) -> AwaitableResultTupleWrapper[_F, _S_default_co]:
        """Apply a synchronous function to the wrapped [trcks.Failure][] object.

        Wrapped [trcks.SuccessTuple][] objects are passed on unchanged.

        Args:
            f: The synchronous function to be applied.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - the result of the function application if
                    the original [trcks.AwaitableResultTuple][] is a failure, or
                - the original [trcks.AwaitableResultTuple][] if it is a success.

        Example:
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
        return AwaitableResultTupleWrapper(art.map_failure(f)(self.core))

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
                    the original [trcks.AwaitableResultTuple][] is a failure, or
                - the original [trcks.AwaitableResultTuple][] if it is a success.

        Example:
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
        return AwaitableResultTupleWrapper(art.map_failure_to_awaitable(f)(self.core))

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
                    the original [trcks.AwaitableResultTuple][] is a failure, or
                - the original [trcks.AwaitableResultTuple][] if it is a success.

        Example:
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
            art.map_failure_to_awaitable_result_iterable(f)(self.core)
        )

    @deprecated("Use map_failure_to_awaitable_result_iterable instead")
    def map_failure_to_awaitable_result_tuple(
        self, f: Callable[[_F_default_co], AwaitableResultTuple[_F, _S]]
    ) -> AwaitableResultTupleWrapper[_F, _S_default_co | _S]:
        """Deprecated alias for
        [trcks.oop.AwaitableResultTupleWrapper.map_failure_to_awaitable_result_iterable][].
        """
        return self.map_failure_to_awaitable_result_iterable(f)  # pragma: no cover

    def map_failure_to_iterable(
        self, f: Callable[[_F_default_co], Iterable[_S]]
    ) -> AwaitableResultTupleWrapper[Never, _S_default_co | _S]:
        """Apply a synchronous function returning an [collections.abc.Iterable][]
        to the wrapped [trcks.Failure][] object.

        Wrapped [trcks.SuccessTuple][] objects are passed on unchanged.

        Args:
            f: The synchronous function returning an
                [collections.abc.Iterable][] to be applied.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - an [trcks.AwaitableSuccessTuple][] containing the result of
                    the function application if
                    the original [trcks.AwaitableResultTuple][] is a failure, or
                - the original [trcks.AwaitableResultTuple][] if it is a success.

        Example:
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
        mapped_f: Callable[
            [AwaitableResultTuple[_F_default_co, _S_default_co]],
            AwaitableResultTuple[Never, _S_default_co | _S],
        ] = art.map_failure_to_iterable(f)
        return AwaitableResultTupleWrapper(mapped_f(self.core))

    def map_failure_to_result(
        self, f: Callable[[_F_default_co], Result[_F, _S]]
    ) -> AwaitableResultTupleWrapper[_F, _S_default_co | _S]:
        """Apply a synchronous function with return type [trcks.Result][]
        to the wrapped [trcks.Failure][] object.

        Wrapped [trcks.SuccessTuple][] objects are passed on unchanged.

        Args:
            f: The synchronous function to be applied.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - the result of the function application if
                    the original [trcks.AwaitableResultTuple][] is a failure, or
                - the original [trcks.AwaitableResultTuple][] if it is a success.

        Example:
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
        return AwaitableResultTupleWrapper(art.map_failure_to_result(f)(self.core))

    def map_failure_to_result_iterable(
        self, f: Callable[[_F_default_co], ResultIterable[_F, _S]]
    ) -> AwaitableResultTupleWrapper[_F, _S_default_co | _S]:
        """Apply a synchronous function with return type [trcks.ResultIterable][]
        to the wrapped [trcks.Failure][] object.

        Wrapped [trcks.SuccessTuple][] objects are passed on unchanged.

        Args:
            f: The synchronous function to be applied.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - the result of the function application if
                    the original [trcks.AwaitableResultTuple][] is a failure, or
                - the original [trcks.AwaitableResultTuple][] if it is a success.

        Example:
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
            art.map_failure_to_result_iterable(f)(self.core)
        )

    @deprecated("Use map_failure_to_result_iterable instead")
    def map_failure_to_result_tuple(
        self, f: Callable[[_F_default_co], ResultTuple[_F, _S]]
    ) -> AwaitableResultTupleWrapper[_F, _S_default_co | _S]:
        """Deprecated alias for
        [trcks.oop.AwaitableResultTupleWrapper.map_failure_to_result_iterable][].
        """
        return self.map_failure_to_result_iterable(f)  # pragma: no cover

    @deprecated("Use map_failure_to_iterable instead")
    def map_failure_to_tuple(
        self, f: Callable[[_F_default_co], tuple[_S, ...]]
    ) -> AwaitableResultTupleWrapper[Never, _S_default_co | _S]:
        """Deprecated alias for
        [trcks.oop.AwaitableResultTupleWrapper.map_failure_to_iterable][].
        """
        return self.map_failure_to_iterable(f)  # pragma: no cover

    def map_successes(
        self, f: Callable[[_S_default_co], _S]
    ) -> AwaitableResultTupleWrapper[_F_default_co, _S]:
        """Apply a synchronous function to each element in the wrapped
        [trcks.AwaitableSuccessTuple][].

        Wrapped [trcks.Failure][] objects are passed on unchanged.

        Args:
            f: The synchronous function to be applied to each success element.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - the original [trcks.AwaitableResultTuple][] if it is a failure,
                    or
                - an [trcks.AwaitableSuccessTuple][] with transformed elements if
                    the original [trcks.AwaitableResultTuple][] is a success.

        Example:
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
        return AwaitableResultTupleWrapper(art.map_successes(f)(self.core))

    def map_successes_to_awaitable(
        self, f: Callable[[_S_default_co], Awaitable[_S]]
    ) -> AwaitableResultTupleWrapper[_F_default_co, _S]:
        """Apply an asynchronous function to each element in the wrapped
        [trcks.AwaitableSuccessTuple][].

        Wrapped [trcks.Failure][] objects are passed on unchanged.

        Args:
            f: The asynchronous function to be applied to each success element.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - the original [trcks.AwaitableResultTuple][] if it is a failure,
                    or
                - an [trcks.AwaitableSuccessTuple][] with transformed elements if
                    the original [trcks.AwaitableResultTuple][] is a success.

        Example:
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
        return AwaitableResultTupleWrapper(art.map_successes_to_awaitable(f)(self.core))

    def map_successes_to_awaitable_result(
        self, f: Callable[[_S_default_co], AwaitableResult[_F, _S]]
    ) -> AwaitableResultTupleWrapper[_F_default_co | _F, _S]:
        """Apply an asynchronous function with return type [trcks.AwaitableResult][]
        to each element in the wrapped [trcks.AwaitableSuccessTuple][].

        Wrapped [trcks.Failure][] objects are passed on unchanged.
        Short-circuits on the first failure returned by the function.

        Args:
            f: The asynchronous function to be applied to each success element.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - the original [trcks.AwaitableResultTuple][] if it is a failure,
                - the first [trcks.Failure][] returned by the function, or
                - an [trcks.AwaitableSuccessTuple][] with all transformed
                    elements if the function returns success for all elements.

        Example:
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
            art.map_successes_to_awaitable_result(f)(self.core)
        )

    def map_successes_to_awaitable_result_iterable(
        self, f: Callable[[_S_default_co], AwaitableResultIterable[_F, _S]]
    ) -> AwaitableResultTupleWrapper[_F_default_co | _F, _S]:
        """Apply an asynchronous function with return type
        [trcks.AwaitableResultIterable][] to each element in the wrapped
        [trcks.AwaitableSuccessTuple][] and flatten.

        Wrapped [trcks.Failure][] objects are passed on unchanged.
        Short-circuits on the first failure returned by the function.

        Args:
            f: The asynchronous function to be applied to each success element.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - the original [trcks.AwaitableResultTuple][] if it is a failure,
                - the first [trcks.Failure][] returned by the function, or
                - a flattened [trcks.AwaitableSuccessTuple][] if the function
                    returns success for all elements.

        Example:
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
            art.map_successes_to_awaitable_result_iterable(f)(self.core)
        )

    @deprecated("Use map_successes_to_awaitable_result_iterable instead")
    def map_successes_to_awaitable_result_tuple(
        self, f: Callable[[_S_default_co], AwaitableResultTuple[_F, _S]]
    ) -> AwaitableResultTupleWrapper[_F_default_co | _F, _S]:
        """Deprecated alias for
        [trcks.oop.AwaitableResultTupleWrapper.map_successes_to_awaitable_result_iterable][].
        """
        return self.map_successes_to_awaitable_result_iterable(f)  # pragma: no cover

    def map_successes_to_iterable(
        self, f: Callable[[_S_default_co], Iterable[_S]]
    ) -> AwaitableResultTupleWrapper[_F_default_co, _S]:
        """Apply a synchronous function returning an [collections.abc.Iterable][]
        to each element in the wrapped [trcks.AwaitableSuccessTuple][] and flatten.

        Wrapped [trcks.Failure][] objects are passed on unchanged.

        Args:
            f: The synchronous function returning an
                [collections.abc.Iterable][] to be applied to each success
                element.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - the original [trcks.AwaitableResultTuple][] if it is a failure,
                    or
                - a flattened [trcks.AwaitableSuccessTuple][] if
                    the original [trcks.AwaitableResultTuple][] is a success.

        Example:
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
        return AwaitableResultTupleWrapper(art.map_successes_to_iterable(f)(self.core))

    def map_successes_to_result(
        self, f: Callable[[_S_default_co], Result[_F, _S]]
    ) -> AwaitableResultTupleWrapper[_F_default_co | _F, _S]:
        """Apply a synchronous function with return type [trcks.Result][]
        to each element in the wrapped [trcks.AwaitableSuccessTuple][].

        Wrapped [trcks.Failure][] objects are passed on unchanged.
        Short-circuits on the first failure returned by the function.

        Args:
            f: The synchronous function to be applied to each success element.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - the original [trcks.AwaitableResultTuple][] if it is a failure,
                - the first [trcks.Failure][] returned by the function, or
                - an [trcks.AwaitableSuccessTuple][] with all transformed
                    elements if the function returns success for all elements.

        Example:
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
        return AwaitableResultTupleWrapper(art.map_successes_to_result(f)(self.core))

    def map_successes_to_result_iterable(
        self, f: Callable[[_S_default_co], ResultIterable[_F, _S]]
    ) -> AwaitableResultTupleWrapper[_F_default_co | _F, _S]:
        """Apply a synchronous function with return type [trcks.ResultIterable][]
        to each element in the wrapped [trcks.AwaitableSuccessTuple][] and flatten.

        Wrapped [trcks.Failure][] objects are passed on unchanged.
        Short-circuits on the first failure returned by the function.

        Args:
            f: The synchronous function to be applied to each success element.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - the original [trcks.AwaitableResultTuple][] if it is a failure,
                - the first [trcks.Failure][] returned by the function, or
                - a flattened [trcks.AwaitableSuccessTuple][] if the function
                    returns success for all elements.

        Example:
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
            art.map_successes_to_result_iterable(f)(self.core)
        )

    @deprecated("Use map_successes_to_result_iterable instead")
    def map_successes_to_result_tuple(
        self, f: Callable[[_S_default_co], ResultTuple[_F, _S]]
    ) -> AwaitableResultTupleWrapper[_F_default_co | _F, _S]:
        """Deprecated alias for
        [trcks.oop.AwaitableResultTupleWrapper.map_successes_to_result_iterable][].
        """
        return self.map_successes_to_result_iterable(f)  # pragma: no cover

    @deprecated("Use map_successes_to_iterable instead")
    def map_successes_to_tuple(
        self, f: Callable[[_S_default_co], tuple[_S, ...]]
    ) -> AwaitableResultTupleWrapper[_F_default_co, _S]:
        """Deprecated alias for
        [trcks.oop.AwaitableResultTupleWrapper.map_successes_to_iterable][].
        """
        return self.map_successes_to_iterable(f)  # pragma: no cover

    def tap_failure(
        self, f: Callable[[_F_default_co], object]
    ) -> AwaitableResultTupleWrapper[_F_default_co, _S_default_co]:
        """Apply a synchronous side effect to the wrapped [trcks.Failure][] object.

        Wrapped [trcks.SuccessTuple][] objects are passed on without side effects.

        Args:
            f: The synchronous side effect to be applied.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance
                with the original [trcks.AwaitableResultTuple][] object,
                allowing for further method chaining.

        Example:
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
        return AwaitableResultTupleWrapper(art.tap_failure(f)(self.core))

    def tap_failure_to_awaitable(
        self, f: Callable[[_F_default_co], Awaitable[object]]
    ) -> AwaitableResultTupleWrapper[_F_default_co, _S_default_co]:
        """Apply an asynchronous side effect to the wrapped [trcks.Failure][] object.

        Wrapped [trcks.SuccessTuple][] objects are passed on without side effects.

        Args:
            f: The asynchronous side effect to be applied.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance
                with the original [trcks.AwaitableResultTuple][] object,
                allowing for further method chaining.

        Example:
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
        return AwaitableResultTupleWrapper(art.tap_failure_to_awaitable(f)(self.core))

    def tap_failure_to_awaitable_result(
        self, f: Callable[[_F_default_co], AwaitableResult[object, _S]]
    ) -> AwaitableResultTupleWrapper[_F_default_co, _S_default_co | _S]:
        """Apply an asynchronous side effect with return type [trcks.AwaitableResult][]
        to the wrapped [trcks.Failure][] object.

        Wrapped [trcks.SuccessTuple][] objects are passed on without side effects.

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
            art.tap_failure_to_awaitable_result(f)(self.core)
        )

    def tap_failure_to_awaitable_result_iterable(
        self, f: Callable[[_F_default_co], AwaitableResultIterable[object, _S]]
    ) -> AwaitableResultTupleWrapper[_F_default_co, _S_default_co | _S]:
        """Apply an asynchronous side effect with return type
        [trcks.AwaitableResultIterable][] to the wrapped [trcks.Failure][] object.

        Wrapped [trcks.SuccessTuple][] objects are passed on without side effects.

        Args:
            f: The asynchronous side effect to be applied.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - *the original* [trcks.Failure][]
                    if the applied side effect returns a [trcks.Failure][],
                - *the returned* [trcks.SuccessTuple][]
                    if the applied side effect returns a [trcks.SuccessTuple][] and
                - *the original* [trcks.SuccessTuple][]
                    if no side effect was applied.

        Example:
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
            art.tap_failure_to_awaitable_result_iterable(f)(self.core)
        )

    @deprecated("Use tap_failure_to_awaitable_result_iterable instead")
    def tap_failure_to_awaitable_result_tuple(
        self, f: Callable[[_F_default_co], AwaitableResultTuple[object, _S]]
    ) -> AwaitableResultTupleWrapper[_F_default_co, _S_default_co | _S]:
        """Deprecated alias for
        [trcks.oop.AwaitableResultTupleWrapper.tap_failure_to_awaitable_result_iterable][].
        """
        return self.tap_failure_to_awaitable_result_iterable(f)  # pragma: no cover

    def tap_failure_to_iterable(
        self, f: Callable[[_F_default_co], Iterable[object]]
    ) -> AwaitableResultTupleWrapper[Never, _F_default_co | _S_default_co]:
        """Apply a synchronous side effect returning an [collections.abc.Iterable][]
        to the wrapped [trcks.Failure][] object.

        The failure is converted to an [trcks.AwaitableSuccessTuple][] where
        the original failure value is repeated once per element in
        the [collections.abc.Iterable][] returned by the side effect.

        Wrapped [trcks.SuccessTuple][] objects are passed on without side effects.

        Args:
            f: The synchronous side effect returning an
                [collections.abc.Iterable][] to be applied.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - an [trcks.AwaitableSuccessTuple][] containing the original
                    failure repeated once per element in the tuple returned by
                    the side effect if the original
                    [trcks.AwaitableResultTuple][] is a failure, or
                - the original [trcks.AwaitableSuccessTuple][]
                    if no side effect was applied.

        Example:
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
        tapped_f: Callable[
            [AwaitableResultTuple[_F_default_co, _S_default_co]],
            AwaitableResultTuple[Never, _F_default_co | _S_default_co],
        ] = art.tap_failure_to_iterable(f)
        return AwaitableResultTupleWrapper(tapped_f(self.core))

    def tap_failure_to_result(
        self, f: Callable[[_F_default_co], Result[object, _S]]
    ) -> AwaitableResultTupleWrapper[_F_default_co, _S_default_co | _S]:
        """Apply a synchronous side effect with return type [trcks.Result][]
        to the wrapped [trcks.Failure][] object.

        Wrapped [trcks.SuccessTuple][] objects are passed on without side effects.

        Args:
            f: The synchronous side effect to be applied.

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
        return AwaitableResultTupleWrapper(art.tap_failure_to_result(f)(self.core))

    def tap_failure_to_result_iterable(
        self, f: Callable[[_F_default_co], ResultIterable[object, _S]]
    ) -> AwaitableResultTupleWrapper[_F_default_co, _S_default_co | _S]:
        """Apply a synchronous side effect with return type [trcks.ResultIterable][]
        to the wrapped [trcks.Failure][] object.

        Wrapped [trcks.SuccessTuple][] objects are passed on without side effects.

        Args:
            f: The synchronous side effect to be applied.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - *the original* [trcks.Failure][]
                    if the applied side effect returns a [trcks.Failure][],
                - *the returned* [trcks.SuccessIterable][]
                    if the applied side effect returns a [trcks.SuccessIterable][] and
                - *the original* [trcks.SuccessTuple][]
                    if no side effect was applied.

        Example:
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
            art.tap_failure_to_result_iterable(f)(self.core)
        )

    @deprecated("Use tap_failure_to_result_iterable instead")
    def tap_failure_to_result_tuple(
        self, f: Callable[[_F_default_co], ResultTuple[object, _S]]
    ) -> AwaitableResultTupleWrapper[_F_default_co, _S_default_co | _S]:
        """Deprecated alias for
        [trcks.oop.AwaitableResultTupleWrapper.tap_failure_to_result_iterable][].
        """
        return self.tap_failure_to_result_iterable(f)  # pragma: no cover

    @deprecated("Use tap_failure_to_iterable instead")
    def tap_failure_to_tuple(
        self, f: Callable[[_F_default_co], tuple[object, ...]]
    ) -> AwaitableResultTupleWrapper[Never, _F_default_co | _S_default_co]:
        """Deprecated alias for
        [trcks.oop.AwaitableResultTupleWrapper.tap_failure_to_iterable][].
        """
        return self.tap_failure_to_iterable(f)  # pragma: no cover

    def tap_successes(
        self, f: Callable[[_S_default_co], object]
    ) -> AwaitableResultTupleWrapper[_F_default_co, _S_default_co]:
        """Apply a synchronous side effect to each element in the wrapped
        [trcks.AwaitableSuccessTuple][].

        Wrapped [trcks.Failure][] objects are passed on without side effects.

        Args:
            f: The synchronous side effect to be applied to each success element.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance
                with the original [trcks.AwaitableResultTuple][] object,
                allowing for further method chaining.

        Example:
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
        return AwaitableResultTupleWrapper(art.tap_successes(f)(self.core))

    def tap_successes_to_awaitable(
        self, f: Callable[[_S_default_co], Awaitable[object]]
    ) -> AwaitableResultTupleWrapper[_F_default_co, _S_default_co]:
        """Apply an asynchronous side effect to each element in the wrapped
        [trcks.AwaitableSuccessTuple][].

        Wrapped [trcks.Failure][] objects are passed on without side effects.

        Args:
            f: The asynchronous side effect to be applied to each success element.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance
                with the original [trcks.AwaitableResultTuple][] object,
                allowing for further method chaining.

        Example:
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
        return AwaitableResultTupleWrapper(art.tap_successes_to_awaitable(f)(self.core))

    def tap_successes_to_awaitable_result(
        self, f: Callable[[_S_default_co], AwaitableResult[_F, object]]
    ) -> AwaitableResultTupleWrapper[_F_default_co | _F, _S_default_co]:
        """Apply an asynchronous side effect with return type [trcks.AwaitableResult][]
        to each element in the wrapped [trcks.AwaitableSuccessTuple][].

        Wrapped [trcks.Failure][] objects are passed on without side effects.

        Args:
            f: The asynchronous side effect to be applied to each success element.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - *the original* [trcks.Failure][] if no side effect was applied,
                - *the returned* [trcks.Failure][]
                    if the applied side effect returns a [trcks.Failure][] and
                - *the original* [trcks.AwaitableSuccessTuple][]
                    if the applied side effect returns success for all elements.

        Example:
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
            art.tap_successes_to_awaitable_result(f)(self.core)
        )

    def tap_successes_to_awaitable_result_iterable(
        self, f: Callable[[_S_default_co], AwaitableResultIterable[_F, object]]
    ) -> AwaitableResultTupleWrapper[_F_default_co | _F, _S_default_co]:
        """Apply an asynchronous side effect with return type
        [trcks.AwaitableResultIterable][] to each element in the wrapped
        [trcks.AwaitableSuccessTuple][].

        Wrapped [trcks.Failure][] objects are passed on without side effects.

        Args:
            f: The asynchronous side effect to be applied to each success element.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - *the original* [trcks.Failure][] if no side effect was applied,
                - *the returned* [trcks.Failure][]
                    if the applied side effect returns a [trcks.Failure][] and
                - *the original* success element repeated once per element
                    in the side effect output if the applied side effect returns
                    success for all elements.

        Example:
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
            art.tap_successes_to_awaitable_result_iterable(f)(self.core)
        )

    @deprecated("Use tap_successes_to_awaitable_result_iterable instead")
    def tap_successes_to_awaitable_result_tuple(
        self, f: Callable[[_S_default_co], AwaitableResultTuple[_F, object]]
    ) -> AwaitableResultTupleWrapper[_F_default_co | _F, _S_default_co]:
        """Deprecated alias for
        [trcks.oop.AwaitableResultTupleWrapper.tap_successes_to_awaitable_result_iterable][].
        """
        return self.tap_successes_to_awaitable_result_iterable(f)  # pragma: no cover

    def tap_successes_to_iterable(
        self, f: Callable[[_S_default_co], Iterable[object]]
    ) -> AwaitableResultTupleWrapper[_F_default_co, _S_default_co]:
        """Apply a synchronous side effect returning an [collections.abc.Iterable][]
        to each element in the wrapped [trcks.AwaitableSuccessTuple][].

        The original success elements are repeated once per element in the
        [collections.abc.Iterable][] returned by the side effect.

        Wrapped [trcks.Failure][] objects are passed on without side effects.

        Args:
            f: The synchronous side effect returning an
                [collections.abc.Iterable][] to be applied
                to each success element.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - the original [trcks.Failure][] if no side effect was applied, or
                - an [trcks.AwaitableSuccessTuple][] where each original element
                    is repeated once per element in the tuple returned by the
                    side effect.

        Example:
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
        return AwaitableResultTupleWrapper(art.tap_successes_to_iterable(f)(self.core))

    def tap_successes_to_result(
        self, f: Callable[[_S_default_co], Result[_F, object]]
    ) -> AwaitableResultTupleWrapper[_F_default_co | _F, _S_default_co]:
        """Apply a synchronous side effect with return type [trcks.Result][]
        to each element in the wrapped [trcks.AwaitableSuccessTuple][].

        Wrapped [trcks.Failure][] objects are passed on without side effects.

        Args:
            f: The synchronous side effect to be applied to each success element.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - *the original* [trcks.Failure][] if no side effect was applied,
                - *the returned* [trcks.Failure][]
                    if the applied side effect returns a [trcks.Failure][] and
                - *the original* [trcks.AwaitableSuccessTuple][]
                    if the applied side effect returns success for all elements.

        Example:
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
        return AwaitableResultTupleWrapper(art.tap_successes_to_result(f)(self.core))

    def tap_successes_to_result_iterable(
        self, f: Callable[[_S_default_co], ResultIterable[_F, object]]
    ) -> AwaitableResultTupleWrapper[_F_default_co | _F, _S_default_co]:
        """Apply a synchronous side effect with return type [trcks.ResultIterable][]
        to each element in the wrapped [trcks.AwaitableSuccessTuple][].

        Wrapped [trcks.Failure][] objects are passed on without side effects.

        Args:
            f: The synchronous side effect to be applied to each success element.

        Returns:
            A new [trcks.oop.AwaitableResultTupleWrapper][] instance with

                - *the original* [trcks.Failure][] if no side effect was applied,
                - *the returned* [trcks.Failure][]
                    if the applied side effect returns a [trcks.Failure][] and
                - *the original* success element repeated once per element
                    in the side effect output if the applied side effect returns
                    success for all elements.

        Example:
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
            art.tap_successes_to_result_iterable(f)(self.core)
        )

    @deprecated("Use tap_successes_to_result_iterable instead")
    def tap_successes_to_result_tuple(
        self, f: Callable[[_S_default_co], ResultTuple[_F, object]]
    ) -> AwaitableResultTupleWrapper[_F_default_co | _F, _S_default_co]:
        """Deprecated alias for
        [trcks.oop.AwaitableResultTupleWrapper.tap_successes_to_result_iterable][].
        """
        return self.tap_successes_to_result_iterable(f)  # pragma: no cover

    @deprecated("Use tap_successes_to_iterable instead")
    def tap_successes_to_tuple(
        self, f: Callable[[_S_default_co], tuple[object, ...]]
    ) -> AwaitableResultTupleWrapper[_F_default_co, _S_default_co]:
        """Deprecated alias for
        [trcks.oop.AwaitableResultTupleWrapper.tap_successes_to_iterable][].
        """
        return self.tap_successes_to_iterable(f)  # pragma: no cover
