"""Object-oriented interface for [trcks][].

This package provides wrapper classes for processing values of the following types
in a method-chaining style:

- [collections.abc.Awaitable][]
- [trcks.AwaitableResult][]
- [trcks.AwaitableResultTuple][]
- [trcks.AwaitableTuple][]
- [trcks.Result][]
- [trcks.ResultTuple][]
- [tuple][]

Example:
    This example uses the classes [trcks.oop.Wrapper][] and [trcks.oop.ResultWrapper][]
    to create and further process a value of type [trcks.Result][]:

    >>> import enum
    >>> import math
    >>> from trcks import Result
    >>> from trcks.oop import Wrapper
    >>> class GetSquareRootError(enum.Enum):
    ...     NEGATIVE_INPUT = enum.auto()
    ...
    >>> def get_square_root(x: float) -> Result[GetSquareRootError, float]:
    ...     return (
    ...         Wrapper(core=x)
    ...         .map_to_result(
    ...             lambda xx: ("success", xx)
    ...             if xx >= 0
    ...             else ("failure", GetSquareRootError.NEGATIVE_INPUT)
    ...         )
    ...         .map_success(math.sqrt)
    ...         .core
    ...     )
    ...
    >>> get_square_root(25.0)
    ('success', 5.0)
    >>> get_square_root(-25.0)
    ('failure', <GetSquareRootError.NEGATIVE_INPUT: 1>)

    Variable and type assignments for intermediate values might help to clarify
    what is going on:

    >>> import enum
    >>> import math
    >>> from trcks import Result
    >>> from trcks.oop import ResultWrapper, Wrapper
    >>> class GetSquareRootError(enum.Enum):
    ...     NEGATIVE_INPUT = enum.auto()
    ...
    >>> def get_square_root(x: float) -> Result[GetSquareRootError, float]:
    ...     wrapper: Wrapper[float] = Wrapper(core=x)
    ...     result_wrapper: ResultWrapper[
    ...         GetSquareRootError, float
    ...     ] = wrapper.map_to_result(
    ...         lambda xx: ("success", xx)
    ...         if xx >= 0
    ...         else ("failure", GetSquareRootError.NEGATIVE_INPUT)
    ...     )
    ...     mapped_result_wrapper: ResultWrapper[GetSquareRootError, float] = (
    ...         result_wrapper.map_success(math.sqrt)
    ...     )
    ...     result: Result[GetSquareRootError, float] = mapped_result_wrapper.core
    ...     return result
    ...
    >>> get_square_root(25.0)
    ('success', 5.0)
    >>> get_square_root(-25.0)
    ('failure', <GetSquareRootError.NEGATIVE_INPUT: 1>)

See:
    - [Method chaining - Wikipedia](https://en.wikipedia.org/w/index.php?title=Method_chaining&oldid=1262555147)
    - [Method Chaining in Python - GeeksforGeeks](https://www.geeksforgeeks.org/method-chaining-in-python/)
"""

from trcks.oop._awaitable_result_tuple_wrapper import AwaitableResultTupleWrapper
from trcks.oop._awaitable_result_wrapper import AwaitableResultWrapper
from trcks.oop._awaitable_tuple_wrapper import AwaitableTupleWrapper
from trcks.oop._awaitable_wrapper import AwaitableWrapper
from trcks.oop._result_tuple_wrapper import ResultTupleWrapper
from trcks.oop._result_wrapper import ResultWrapper
from trcks.oop._tuple_wrapper import TupleWrapper
from trcks.oop._wrapper import Wrapper

__all__ = [
    "AwaitableResultTupleWrapper",
    "AwaitableResultWrapper",
    "AwaitableTupleWrapper",
    "AwaitableWrapper",
    "ResultTupleWrapper",
    "ResultWrapper",
    "TupleWrapper",
    "Wrapper",
]
__docformat__ = "google"
