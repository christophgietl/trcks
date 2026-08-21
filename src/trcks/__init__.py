"""Type-safe railway-oriented programming (ROP).

This package provides generic type aliases needed for ROP (see "Attributes" section).
It also provides modules for doing ROP in a functional style or
in an object-oriented style (see "Modules" section).

Modules:
    fp: Functions for doing ROP in a functional style.
    oop: Classes for doing ROP in an object-oriented style.

Attributes:
    AwaitableFailure: Awaitable that yields a [trcks.Failure][].
    AwaitableIterable: Awaitable that yields a [collections.abc.Iterable][].
    AwaitableResult: Awaitable that yields a [trcks.Result][].
    AwaitableResultIterable: Awaitable that yields a [trcks.ResultIterable][].
    AwaitableResultTuple: Awaitable that yields a [trcks.ResultTuple][].
    AwaitableSuccess: Awaitable that yields a [trcks.Success][].
    AwaitableSuccessIterable: Awaitable that yields a [trcks.SuccessIterable][].
    AwaitableSuccessTuple: Awaitable that yields a [trcks.SuccessTuple][].
    AwaitableTuple: Awaitable that yields a homogeneous [tuple][].
    Failure: [tuple][] containing ``"failure"`` and a value of type `_F_co`.
    Result: Union of [trcks.Failure][] and [trcks.Success][].
    ResultIterable: [trcks.Result][] with a [collections.abc.Iterable][] success.
    ResultTuple: [trcks.Result][] with a homogeneous [tuple][] success.
    Success: [tuple][] containing ``"success"`` and a value of type `_S_co`.
    SuccessIterable: [trcks.Success][] containing a [collections.abc.Iterable][].
    SuccessTuple: [trcks.Success][] containing a homogeneous [tuple][].

Examples:
    Construct a `Failure`:

    >>> failure: Failure[str] = ("failure", "File does not exist")

    Construct a `Success`:

    >>> success: Success[int] = ("success", 42)

    Use `Result` as the return type of a function:

    >>> def divide(a: float, b: float) -> Result[ZeroDivisionError, float]:
    ...     try:
    ...         return "success", a / b
    ...     except ZeroDivisionError as e:
    ...         return "failure", e
    ...
    >>> divide(5.0, 2.0)
    ('success', 2.5)
    >>> divide(3.5, 0.0)
    ('failure', ZeroDivisionError('...division by zero'))

    Use `AwaitableResult` to annotate an unawaited `async` function return:

    >>> import asyncio
    >>> async def divide_slowly(a: float, b: float) -> Result[ZeroDivisionError, float]:
    ...     await asyncio.sleep(0.001)
    ...     try:
    ...         return "success", a / b
    ...     except ZeroDivisionError as e:
    ...         return "failure", e
    ...
    >>> async def main() -> None:
    ...     a_rslt: AwaitableResult[ZeroDivisionError, float] = (
    ...         divide_slowly(3.0, 0.0)
    ...     )
    ...     rslt: Result[ZeroDivisionError, float] = await a_rslt
    ...     print(rslt)
    ...
    >>> asyncio.run(main())
    ('failure', ZeroDivisionError('...division by zero'))

    Use `AwaitableResult` to annotate an `async` function
    as a [collections.abc.Callable][]:

    >>> from collections.abc import Callable
    >>>
    >>> copy_of_divide_slowly: Callable[
    ...     [float, float], AwaitableResult[ZeroDivisionError, float]
    ... ] = divide_slowly

Note:
    [trcks.Failure][], [trcks.Success][], and [trcks.Result][] are called
    "Left", "Right", and "Either", respectively, in some functional programming
    languages and packages (e.g. Haskell and fp-ts).

See:
    [Railway oriented programming | F# for fun and profit](https://fsharpforfunandprofit.com/posts/recipe-part2/)
"""

from collections.abc import Awaitable, Iterable
from typing import Literal, TypeAlias

from trcks._typing import TypeVar

__docformat__ = "google"


_F_co = TypeVar("_F_co", covariant=True)
_S_co = TypeVar("_S_co", covariant=True)
_T_co = TypeVar("_T_co", covariant=True)


Failure: TypeAlias = tuple[Literal["failure"], _F_co]
Success: TypeAlias = tuple[Literal["success"], _S_co]
Result: TypeAlias = Failure[_F_co] | Success[_S_co]
ResultIterable: TypeAlias = Result[_F_co, Iterable[_S_co]]
ResultTuple: TypeAlias = Result[_F_co, tuple[_S_co, ...]]
SuccessIterable: TypeAlias = Success[Iterable[_S_co]]
SuccessTuple: TypeAlias = Success[tuple[_S_co, ...]]
AwaitableFailure: TypeAlias = Awaitable[Failure[_F_co]]
AwaitableIterable: TypeAlias = Awaitable[Iterable[_T_co]]
AwaitableResult: TypeAlias = Awaitable[Result[_F_co, _S_co]]
AwaitableResultIterable: TypeAlias = Awaitable[ResultIterable[_F_co, _S_co]]
AwaitableResultTuple: TypeAlias = Awaitable[ResultTuple[_F_co, _S_co]]
AwaitableSuccess: TypeAlias = Awaitable[Success[_S_co]]
AwaitableSuccessIterable: TypeAlias = Awaitable[SuccessIterable[_S_co]]
AwaitableSuccessTuple: TypeAlias = Awaitable[SuccessTuple[_S_co]]
AwaitableTuple: TypeAlias = Awaitable[tuple[_T_co, ...]]
