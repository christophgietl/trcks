from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING, Literal

from trcks import AwaitableResult, Result
from trcks._typing import Never, TypeVar
from trcks.fp.monads import awaitable_result
from trcks.oop._base_awaitable_wrapper import BaseAwaitableWrapper

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Awaitable, Callable

__docformat__ = "google"

_F = TypeVar("_F")
_S = TypeVar("_S")

_F_co = TypeVar("_F_co", covariant=True, default=Never)
_S_co = TypeVar("_S_co", covariant=True, default=Never)


@dataclasses.dataclass(frozen=True)
class AwaitableResultWrapper(BaseAwaitableWrapper[Result[_F_co, _S_co]]):
    """Typesafe and immutable wrapper for `trcks.AwaitableResult` objects.

    The wrapped object can be accessed via the attribute `AwaitableResultWrapper.core`.
    The ``AwaitableResultWrapper.map*`` methods allow method chaining.

    Attributes:
        core: The wrapped `trcks.AwaitableResult` object.
        core_as_coroutine:
            The wrapped `trcks.AwaitableResult` object transformed into a coroutine.

    Example:
        >>> import asyncio
        >>> import math
        >>> from trcks import Result
        >>> from trcks.oop import AwaitableResultWrapper
        >>> async def read_from_disk() -> Result[str, float]:
        ...     await asyncio.sleep(0.001)
        ...     return ("failure", "not found")
        ...
        >>> def get_square_root(x: float) -> Result[str, float]:
        ...     if x < 0:
        ...         return ("failure", "negative value")
        ...     return ("success", math.sqrt(x))
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
            the wrapped ``collections.abc.Awaitable[trcks.Failure]`` object.

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
        return AwaitableResultWrapper(awaitable_result.construct_failure(value))

    @staticmethod
    def construct_failure_from_awaitable(
        awtbl: Awaitable[_F],
    ) -> AwaitableResultWrapper[_F, Never]:
        """Construct and wrap an awaitable `trcks.Failure` from an awaitable value.

        Args:
            awtbl: The awaitable value to be wrapped.

        Returns:
            A new `AwaitableResultWrapper` instance with
            the wrapped ``collections.abc.Awaitable[trcks.Failure]`` object.

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
        return AwaitableResultWrapper(
            awaitable_result.construct_failure_from_awaitable(awtbl)
        )

    @staticmethod
    def construct_from_awaitable_result(
        a_rslt: AwaitableResult[_F, _S],
    ) -> AwaitableResultWrapper[_F, _S]:
        """Wrap an awaitable `trcks.Result` object.

        Args:
            a_rslt: The awaitable `trcks.Result` object to be wrapped.

        Returns:
            A new `AwaitableResultWrapper` instance with
            the wrapped ``collections.abc.Awaitable[trcks.Result]`` object.

        Example:
            >>> import asyncio
            >>> from trcks import Result
            >>> from trcks.oop import AwaitableResultWrapper
            >>> async def read_from_disk() -> Result[str, str]:
            ...     await asyncio.sleep(0.001)
            ...     return ("failure", "file not found")
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
    def construct_from_result(rslt: Result[_F, _S]) -> AwaitableResultWrapper[_F, _S]:
        """Construct and wrap an awaitbl. `trcks.Result` obj. from a `trcks.Result` obj.

        Args:
            rslt: The `trcks.Result` object to be wrapped.

        Returns:
            A new `AwaitableResultWrapper` instance with
            the wrapped ``collections.abc.Awaitable[trcks.Result]`` object.

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
        return AwaitableResultWrapper(awaitable_result.construct_from_result(rslt))

    @staticmethod
    def construct_success(value: _S) -> AwaitableResultWrapper[Never, _S]:
        """Construct and wrap an awaitable `trcks.Success` object from a value.

        Args:
            value: The value to be wrapped.

        Returns:
            A new `AwaitableResultWrapper` instance with
            the wrapped ``collections.abc.Awaitable[trcks.Success]`` object.

        Example:
            >>> import asyncio
            >>> from trcks.oop import AwaitableResultWrapper
            >>> awaitable_result_wrapper = AwaitableResultWrapper.construct_success(42)
            >>> awaitable_result_wrapper
            AwaitableResultWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_result_wrapper.core_as_coroutine)
            ('success', 42)
        """
        return AwaitableResultWrapper(awaitable_result.construct_success(value))

    @staticmethod
    def construct_success_from_awaitable(
        awtbl: Awaitable[_S],
    ) -> AwaitableResultWrapper[Never, _S]:
        """Construct and wrap an awaitable `trcks.Success` from an awaitable value.

        Args:
            awtbl: The awaitable value to be wrapped.

        Returns:
            A new `AwaitableResultWrapper` instance with
            the wrapped ``collections.abc.Awaitable[trcks.Success]`` object.

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
        return AwaitableResultWrapper(
            awaitable_result.construct_success_from_awaitable(awtbl)
        )

    def map_failure(
        self, f: Callable[[_F_co], _F]
    ) -> AwaitableResultWrapper[_F, _S_co]:
        """Apply sync. func. to wrapped `trcks.AwaitableResult` obj. if it is a failure.

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
        f_mapped = awaitable_result.map_failure(f)
        return AwaitableResultWrapper(f_mapped(self.core))

    def map_failure_to_awaitable(
        self, f: Callable[[_F_co], Awaitable[_F]]
    ) -> AwaitableResultWrapper[_F, _S_co]:
        """Apply async. func. to wrapped `trcks.AwaitableResult` obj. if failure.

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
        f_mapped = awaitable_result.map_failure_to_awaitable(f)
        return AwaitableResultWrapper(f_mapped(self.core))

    def map_failure_to_awaitable_result(
        self, f: Callable[[_F_co], AwaitableResult[_F, _S]]
    ) -> AwaitableResultWrapper[_F, _S_co | _S]:
        """Apply async. `trcks.Result` func. to `trcks.AwaitableResult` if failure.

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
            ...         return ("success", 0)
            ...     return ("failure", s)
            ...
            >>> awaitable_result_wrapper_1 = (
            ...     AwaitableResultWrapper
            ...     .construct_failure("not found")
            ...     .map_failure_to_awaitable_result(slowly_replace_not_found)
            ... )
            >>> awaitable_result_wrapper_1
            AwaitableResultWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_result_wrapper_1.core_as_coroutine)
            ('success', 0)
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
        f_mapped = awaitable_result.map_failure_to_awaitable_result(f)
        return AwaitableResultWrapper(f_mapped(self.core))

    def map_failure_to_result(
        self, f: Callable[[_F_co], Result[_F, _S]]
    ) -> AwaitableResultWrapper[_F, _S_co | _S]:
        """Apply sync. `trcks.Result` func. to `trcks.AwaitableResult` if failure.

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
            ...         return ("success", 0)
            ...     return ("failure", s)
            ...
            >>> awaitable_result_wrapper_1 = (
            ...     AwaitableResultWrapper
            ...     .construct_failure("not found")
            ...     .map_failure_to_result(replace_not_found_by_default_value)
            ... )
            >>> awaitable_result_wrapper_1
            AwaitableResultWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_result_wrapper_1.core_as_coroutine)
            ('success', 0)
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
        f_mapped = awaitable_result.map_failure_to_result(f)
        return AwaitableResultWrapper(f_mapped(self.core))

    def map_success(
        self, f: Callable[[_S_co], _S]
    ) -> AwaitableResultWrapper[_F_co, _S]:
        """Apply sync. func. to wrapped `trcks.AwaitableResult` obj. if success.

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
        f_mapped = awaitable_result.map_success(f)
        return AwaitableResultWrapper(f_mapped(self.core))

    def map_success_to_awaitable(
        self, f: Callable[[_S_co], Awaitable[_S]]
    ) -> AwaitableResultWrapper[_F_co, _S]:
        """Apply async. func. to wrapped `trcks.AwaitableResult` obj. if success.

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
        f_mapped = awaitable_result.map_success_to_awaitable(f)
        return AwaitableResultWrapper(f_mapped(self.core))

    def map_success_to_awaitable_result(
        self, f: Callable[[_S_co], AwaitableResult[_F, _S]]
    ) -> AwaitableResultWrapper[_F_co | _F, _S]:
        """Apply async. `trcks.Result` func. to `trcks.AwaitableResult` if success.

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
            ...         return ("failure", "negative value")
            ...     return ("success", math.sqrt(x))
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
        f_mapped = awaitable_result.map_success_to_awaitable_result(f)
        return AwaitableResultWrapper(f_mapped(self.core))

    def map_success_to_result(
        self, f: Callable[[_S_co], Result[_F, _S]]
    ) -> AwaitableResultWrapper[_F_co | _F, _S]:
        """Apply sync. `trcks.Result` func. to `trcks.AwaitableResult` if success.

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
            ...         return ("failure", "negative value")
            ...     return ("success", math.sqrt(x))
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
        f_mapped = awaitable_result.map_success_to_result(f)
        return AwaitableResultWrapper(f_mapped(self.core))

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
    async def value(self) -> _F_co | _S_co:
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
