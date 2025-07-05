"""Functional interface for `trcks`.

This package provides functions for processing values of the following generic types
in a functional style:

- `collections.abc.Awaitable`
- `trcks.AwaitableResult`
- `trcks.Result`

Example:
    This example uses the modules `trcks.fp.composition` and `trcks.fp.monads.result`
    to create and further process a value of type `trcks.Result`:

        >>> import math
        >>> from typing import Literal
        >>> from trcks import Result
        >>> from trcks.fp.composition import pipe
        >>> from trcks.fp.monads import result as r
        >>> GetSquareRootResult = Result[Literal["negative value"], float]
        >>> def get_square_root(x: float) -> GetSquareRootResult:
        ...     return pipe(
        ...         (
        ...             x,
        ...             lambda xx:
        ...                 ("success", xx)
        ...                 if xx >= 0
        ...                 else ("failure", "negative value"),
        ...             r.map_success(math.sqrt),
        ...         )
        ...     )
        ...
        >>> get_square_root(25.0)
        ('success', 5.0)
        >>> get_square_root(-25.0)
        ('failure', 'negative value')

    If your static type checker cannot infer the type of
    the argument passed to `trcks.fp.composition.pipe`,
    you can explicitly assign a type:

        >>> import math
        >>> from typing import Literal
        >>> from trcks import Result
        >>> from trcks.fp.composition import Pipeline2, pipe
        >>> from trcks.fp.monads import result as r
        >>> GetSquareRootResult = Result[Literal["negative value"], float]
        >>> def get_square_root(x: float) -> GetSquareRootResult:
        ...     p: Pipeline2[float, GetSquareRootResult, GetSquareRootResult] = (
        ...         x,
        ...         lambda xx:
        ...             ("success", xx)
        ...             if xx >= 0
        ...             else ("failure", "negative value"),
        ...         r.map_success(math.sqrt),
        ...     )
        ...     return pipe(p)
        ...
        >>> get_square_root(25.0)
        ('success', 5.0)
        >>> get_square_root(-25.0)
        ('failure', 'negative value')
"""

__docformat__ = "google"
