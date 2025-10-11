"""Type-safe railway-oriented programming (ROP).

This package provides

- the generic (return) types [trcks.Result][] and [trcks.AwaitableResult][] and
- the subpackages [trcks.fp][] and [trcks.oop][] for working with these types
  in a functional and object-oriented way, respectively.

See:
    [Railway oriented programming | F# for fun and profit](https://fsharpforfunandprofit.com/posts/recipe-part2/)
"""

from collections.abc import Awaitable
from typing import Literal, TypeAlias

from trcks._typing import TypeVar

__docformat__ = "google"


_F_co = TypeVar("_F_co", covariant=True)
_S_co = TypeVar("_S_co", covariant=True)


Failure: TypeAlias = tuple[Literal["failure"], _F_co]
"""[tuple][] of length 2 containing ``"failure"`` followed by a value of type `_F_co`.

Example:
    >>> failure: Failure[str] = ("failure", "File does not exist")

Note:
    This generic type is called "Left" in
    some functional programming languages and packages (e.g. Haskell and fp-ts).
"""

Success: TypeAlias = tuple[Literal["success"], _S_co]
"""[tuple][] of length 2 containing ``"success"`` followed by a value of type `_S_co`.

Example:
    >>> success: Success[int] = ("success", 42)

Note:
    This generic type is called "Right" in
    some functional programming languages and packages (e.g. Haskell and fp-ts).
"""

Result: TypeAlias = Failure[_F_co] | Success[_S_co]
"""Discriminated union of the generic types `_F_co` and `_S_co`.

Can be used as a return type of a function
instead of returning `_S_co` and raising `_F_co`.

Example:
    >>> def divide(a: float, b: float) -> Result[ZeroDivisionError, float]:
    ...     try:
    ...         return ("success", a/b)
    ...     except ZeroDivisionError as e:
    ...         return ("failure", e)
    ...
    >>> divide(5.0, 2.0)
    ('success', 2.5)
    >>> divide(3.5, 0.0)
    ('failure', ZeroDivisionError('float division by zero'))

Note:
    This generic type is called "Either" in
    some functional programming languages and packages (e.g. Haskell and fp-ts).
"""

AwaitableFailure: TypeAlias = Awaitable[Failure[_F_co]]
"""[collections.abc.Awaitable][] that returns a [trcks.Failure][]
when used in an `await` expression.
"""

AwaitableSuccess: TypeAlias = Awaitable[Success[_S_co]]
"""[collections.abc.Awaitable][] that returns a [trcks.Success][]
when used in an `await` expression.
"""

AwaitableResult: TypeAlias = Awaitable[Result[_F_co, _S_co]]
"""[collections.abc.Awaitable][] that returns a [trcks.Result][]
when used in an `await` expression.

Example:
    Can be used to annotate the non-awaited return value of an `async` function:

    >>> import asyncio
    >>> async def divide_slowly(
    ...     a: float, b: float
    ... ) -> Result[ZeroDivisionError, float]:
    ...     await asyncio.sleep(0.001)
    ...     try:
    ...         return ("success", a / b)
    ...     except ZeroDivisionError as e:
    ...         return ("failure", e)
    ...
    >>> async def main() -> None:
    ...     a_rslt: AwaitableResult[ZeroDivisionError, float] = (
    ...         divide_slowly(3.0, 0.0)
    ...     )
    ...     rslt: Result[ZeroDivisionError, float] = await a_rslt
    ...     print(rslt)
    ...
    >>> asyncio.run(main())
    ('failure', ZeroDivisionError('float division by zero'))

    Can also be used to annotate an `async` function:

    >>> import asyncio
    >>> from collections.abc import Callable
    >>>
    >>> async def divide_slowly(
    ...     a: float, b: float
    ... ) -> Result[ZeroDivisionError, float]:
    ...     await asyncio.sleep(0.001)
    ...     try:
    ...         return ("success", a / b)
    ...     except ZeroDivisionError as e:
    ...         return ("failure", e)
    ...
    >>> copy_of_divide_slowly: Callable[
    ...     [float, float], AwaitableResult[ZeroDivisionError, float]
    ... ] = divide_slowly
"""
