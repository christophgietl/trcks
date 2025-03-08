"""Typesafe railway oriented programming (ROP).

This package provides

- the generic (return) types `trcks.Result` and `trcks.AwaitableResult` and
- the subpackages `trcks.fp` and `trcks.oop` for working with these types
  in a functional and object-oriented way, respectively.

See:
    https://fsharpforfunandprofit.com/posts/recipe-part2/
"""

from trcks._type_aliases import (
    AwaitableFailure,
    AwaitableResult,
    AwaitableSuccess,
    Failure,
    Result,
    Success,
)

__all__ = [
    "AwaitableFailure",
    "AwaitableResult",
    "AwaitableSuccess",
    "Failure",
    "Result",
    "Success",
]
__docformat__ = "google"
