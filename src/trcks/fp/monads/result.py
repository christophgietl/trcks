"""Monadic functions for [trcks.Result][].

Provides utilities for functional composition of
synchronous [trcks.Result][]-returning functions.

Example:
    Create and process a value of type [trcks.Result][]:

    >>> import math
    >>> from trcks.fp.composition import pipe
    >>> from trcks.fp.monads import result as r
    >>> rslt = pipe(
    ...     (
    ...         r.construct_success(1_000_000.0),
    ...         r.tap_success(lambda x: print(f"Processing value {x} ...")),
    ...         r.map_success_to_result(
    ...             lambda x: (
    ...                 ("success", math.sqrt(x))
    ...                 if x >= 0
    ...                 else ("failure", "negative value")
    ...             )
    ...         ),
    ...         r.tap_success_to_result(
    ...             lambda x: (
    ...                 ("success", print(f"Wrote result {x} to disk."))
    ...                 if x < 100
    ...                 else ("failure", "out of disk space")
    ...             )
    ...         ),
    ...     )
    ... )
    Processing value 1000000.0 ...
    >>> rslt
    ('failure', 'out of disk space')

    If your static type checker cannot infer the type of
    the argument passed to [trcks.fp.composition.pipe][],
    you can explicitly assign a type:

    >>> import math
    >>> from trcks import Result, Success
    >>> from trcks.fp.composition import Pipeline3, pipe
    >>> from trcks.fp.monads import result as r
    >>> p: Pipeline3[
    ...     Success[float],
    ...     Result[str, float],
    ...     Result[str, float],
    ...     Result[str, float],
    ... ] = (
    ...     r.construct_success(1_000_000.0),
    ...     r.tap_success(lambda x: print(f"Processing value {x} ...")),
    ...     r.map_success_to_result(
    ...         lambda x: (
    ...             ("success", math.sqrt(x))
    ...             if x >= 0
    ...             else ("failure", "negative value")
    ...         )
    ...     ),
    ...     r.tap_success_to_result(
    ...         lambda x: (
    ...             ("success", print(f"Wrote result {x} to disk."))
    ...             if x < 100
    ...             else ("failure", "out of disk space")
    ...         )
    ...     ),
    ... )
    >>> rslt = pipe(p)
    Processing value 1000000.0 ...
    >>> rslt
    ('failure', 'out of disk space')
"""

from __future__ import annotations

from trcks.fp._monads.result import (
    construct_failure,
    construct_success,
    map_failure,
    map_failure_to_result,
    map_success,
    map_success_to_result,
    tap_failure,
    tap_failure_to_result,
    tap_success,
    tap_success_to_result,
)

__all__ = [
    "construct_failure",
    "construct_success",
    "map_failure",
    "map_failure_to_result",
    "map_success",
    "map_success_to_result",
    "tap_failure",
    "tap_failure_to_result",
    "tap_success",
    "tap_success_to_result",
]
__docformat__ = "google"

# Re-assign __module__ to match the facade module name for test compatibility
construct_failure.__module__ = __name__
construct_success.__module__ = __name__
map_failure.__module__ = __name__
map_failure_to_result.__module__ = __name__
map_success.__module__ = __name__
map_success_to_result.__module__ = __name__
tap_failure.__module__ = __name__
tap_failure_to_result.__module__ = __name__
tap_success.__module__ = __name__
tap_success_to_result.__module__ = __name__
