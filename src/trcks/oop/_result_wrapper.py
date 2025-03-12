from __future__ import annotations

import dataclasses
from typing import TYPE_CHECKING, Literal

from trcks import AwaitableResult, Result
from trcks._typing import Never, TypeVar
from trcks.fp.monads import result
from trcks.oop._awaitable_result_wrapper import AwaitableResultWrapper
from trcks.oop._base_wrapper import BaseWrapper

if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import Awaitable, Callable

__docformat__ = "google"

_F = TypeVar("_F")
_S = TypeVar("_S")

_F_co = TypeVar("_F_co", covariant=True, default=Never)
_S_co = TypeVar("_S_co", covariant=True, default=Never)


@dataclasses.dataclass(frozen=True)
class ResultWrapper(BaseWrapper[Result[_F_co, _S_co]]):
    """Typesafe and immutable wrapper for `trcks.Result` objects.

    The wrapped object can be accessed via the attribute `ResultWrapper.core`.
    The ``ResultWrapper.map*`` methods allow method chaining.

    Attributes:
        core: The wrapped `trcks.Result` object.

    Example:
        >>> import math
        >>> from trcks.oop import ResultWrapper
        >>> result_wrapper = (
        ...     ResultWrapper
        ...     .construct_success(-5.0)
        ...     .map_success_to_result(
        ...         lambda x: ("success", x)
        ...         if x >= 0
        ...         else ("failure", "negative value")
        ...     )
        ...     .map_success(math.sqrt)
        ... )
        >>> result_wrapper
        ResultWrapper(core=('failure', 'negative value'))
        >>> result_wrapper.core
        ('failure', 'negative value')
    """

    @staticmethod
    def construct_failure(value: _F) -> ResultWrapper[_F, Never]:
        """Construct and wrap a `trcks.Failure` object from a value.

        Args:
            value: The value to be wrapped.

        Returns:
            A new `ResultWrapper` instance with the wrapped `trcks.Failure` object.

        Example:
            >>> ResultWrapper.construct_failure(42)
            ResultWrapper(core=('failure', 42))
        """
        return ResultWrapper(result.construct_failure(value))

    @staticmethod
    def construct_from_result(rslt: Result[_F, _S]) -> ResultWrapper[_F, _S]:
        """Wrap a `trcks.Result` object.

        Args:
            rslt: The `trcks.Result` object to be wrapped.

        Returns:
            A new `ResultWrapper` instance with the wrapped `trcks.Result` object.

        Example:
            >>> ResultWrapper.construct_from_result(("success", 0.0))
            ResultWrapper(core=('success', 0.0))
        """
        return ResultWrapper(rslt)

    @staticmethod
    def construct_success(value: _S) -> ResultWrapper[Never, _S]:
        """Construct and wrap a `trcks.Success` object from a value.

        Args:
            value: The value to be wrapped.

        Returns:
            A new `ResultWrapper` instance with the wrapped `trcks.Success` object.

        Example:
            >>> ResultWrapper.construct_success(42)
            ResultWrapper(core=('success', 42))
        """
        return ResultWrapper(result.construct_success(value))

    def map_failure(self, f: Callable[[_F_co], _F]) -> ResultWrapper[_F, _S_co]:
        """Apply sync. func. to the wrapped `trcks.Result` object if it is a failure.

        Args:
            f: The synchronous function to be applied.

        Returns:
            A new `ResultWrapper` instance with

            - the result of the function application if
              the original `trcks.Result` is a failure, or
            - the original `trcks.Result` object if it is a success.

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
        f_mapped = result.map_failure(f)
        return ResultWrapper(f_mapped(self.core))

    def map_failure_to_awaitable(
        self, f: Callable[[_F_co], Awaitable[_F]]
    ) -> AwaitableResultWrapper[_F, _S_co]:
        """Apply async. func. to the wrapped `trcks.Result` object if it is a failure.

        Args:
            f: The asynchronous function to be applied.

        Returns:
            An `AwaitableResultWrapper` instance with

            - the result of the function application if
              the original `trcks.Result` is a failure, or
            - the original `trcks.Result` object if it is a success.

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
        self, f: Callable[[_F_co], AwaitableResult[_F, _S]]
    ) -> AwaitableResultWrapper[_F, _S_co | _S]:
        """Apply async. `trcks.Result` func. to wrapped `trcks.Result` obj. if failure.

        Args:
            f: The asynchronous function to be applied.

        Returns:
            An `AwaitableResultWrapper` instance with

            - the result of the function application if
              the original `trcks.Result` is a failure, or
            - the original `trcks.Result` object if it is a success.

        Example:
            >>> import asyncio
            >>> from trcks import Result
            >>> from trcks.oop import ResultWrapper
            >>> async def slowly_replace_not_found(s: str) -> Result[str, float]:
            ...     await asyncio.sleep(0.001)
            ...     if s == "not found":
            ...         return ("success", 0)
            ...     return ("failure", s)
            ...
            >>> awaitable_result_wrapper_1 = (
            ...     ResultWrapper
            ...     .construct_failure("not found")
            ...     .map_failure_to_awaitable_result(slowly_replace_not_found)
            ... )
            >>> awaitable_result_wrapper_1
            AwaitableResultWrapper(core=<coroutine object ...>)
            >>> asyncio.run(awaitable_result_wrapper_1.core_as_coroutine)
            ('success', 0)
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

    def map_failure_to_result(
        self, f: Callable[[_F_co], Result[_F, _S]]
    ) -> ResultWrapper[_F, _S_co | _S]:
        """Apply sync. `trcks.Result` func. to wrapped `trcks.Result` obj. if failure.

        Args:
            f: The synchronous function to be applied.

        Returns:
            A new `ResultWrapper` instance with

            - the result of the function application if
              the original `trcks.Result` is a failure, or
            - the original `trcks.Result` object if it is a success.

        Example:
            >>> from trcks import Result
            >>> from trcks.oop import ResultWrapper
            >>> def replace_not_found_by_default_value(s: str) -> Result[str, float]:
            ...     if s == "not found":
            ...         return ("success", 0)
            ...     return ("failure", s)
            ...
            >>> ResultWrapper.construct_failure(
            ...     "not found"
            ... ).map_failure_to_result(
            ...     replace_not_found_by_default_value
            ... )
            ResultWrapper(core=('success', 0))
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
        f_mapped = result.map_failure_to_result(f)
        return ResultWrapper(f_mapped(self.core))

    def map_success(self, f: Callable[[_S_co], _S]) -> ResultWrapper[_F_co, _S]:
        """Apply sync. func. to the wrapped `trcks.Result` object if it is a success.

        Args:
            f: The synchronous function to be applied.

        Returns:
            A new `ResultWrapper` instance with

            - the original `trcks.Result` object if it is a failure, or
            - the result of the function application if
              the original `trcks.Result` is a success.

        Example:
            >>> ResultWrapper.construct_failure("not found").map_success(lambda n: n+1)
            ResultWrapper(core=('failure', 'not found'))
            >>>
            >>> ResultWrapper.construct_success(42).map_success(lambda n: n+1)
            ResultWrapper(core=('success', 43))
        """
        f_mapped = result.map_success(f)
        return ResultWrapper(f_mapped(self.core))

    def map_success_to_awaitable(
        self, f: Callable[[_S_co], Awaitable[_S]]
    ) -> AwaitableResultWrapper[_F_co, _S]:
        """Apply async. func. to the wrapped `trcks.Result` object if it is a success.

        Args:
            f: The asynchronous function to be applied.

        Returns:
            An `AwaitableResultWrapper` instance with

            - the original `trcks.Result` object if it is a failure, or
            - the result of the function application if
              the original `trcks.Result` is a success.

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
        self, f: Callable[[_S_co], AwaitableResult[_F, _S]]
    ) -> AwaitableResultWrapper[_F_co | _F, _S]:
        """Apply async. `trcks.Result` func. to wrapped `trcks.Result` obj. if success.

        Args:
            f: The asynchronous function to be applied.

        Returns:
            An `AwaitableResultWrapper` instance with

            - the original `trcks.Result` object if it is a failure, or
            - the result of the function application if
              the original `trcks.Result` is a success.

        Example:
            >>> import asyncio
            >>> import math
            >>> from trcks import Result
            >>> from trcks.oop import ResultWrapper
            >>> async def get_square_root_slowly(x: float) -> Result[str, float]:
            ...     await asyncio.sleep(0.001)
            ...     if x < 0:
            ...         return ("failure", "negative value")
            ...     return ("success", math.sqrt(x))
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

    def map_success_to_result(
        self, f: Callable[[_S_co], Result[_F, _S]]
    ) -> ResultWrapper[_F_co | _F, _S]:
        """Apply sync. `trcks.Result` func. to wrapped `trcks.Result` obj. if success.

        Args:
            f: The synchronous function to be applied.

        Returns:
            A new `ResultWrapper` instance with

            - the original `trcks.Result` object if it is a failure, or
            - the result of the function application if
              the original `trcks.Result` is a success.

        Example:
            >>> import math
            >>> from trcks import Result
            >>> from trcks.oop import ResultWrapper
            >>> def get_square_root(x: float) -> Result[str, float]:
            ...     if x < 0:
            ...         return ("failure", "negative value")
            ...     return ("success", math.sqrt(x))
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
        f_mapped = result.map_success_to_result(f)
        return ResultWrapper(f_mapped(self.core))

    @property
    def track(self) -> Literal["failure", "success"]:
        """First element of the attribute `ResultWrapper.core`.

        Example:
            >>> ResultWrapper(core=('failure', 42)).track
            'failure'
        """
        return self.core[0]

    @property
    def value(self) -> _F_co | _S_co:
        """Second element of the attribute `ResultWrapper.core`.

        Example:
            >>> ResultWrapper(core=('failure', 42)).value
            42
        """
        return self.core[1]
