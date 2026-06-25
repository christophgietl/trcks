"""Helper functions for structural pattern matching."""

from trcks._typing import Never

__docformat__ = "google"


def construct_type_error(_subject: Never, /, *args: object) -> TypeError:
    """Construct a type error for unreachable default cases in pattern matching.

    Args:
        _subject: Subject of the match statement. This argument is ignored.
        args: Arguments for the type error.

    Returns:
        Exception based on `args`.

    Note:
        The argument `_subject` is annotated as `Never`.
        This way, static type checkers can verify that this case is unreachable.

    Example:
        >>> from typing import cast
        >>> def handle_str_or_int(value: str | int) -> None:
        ...     match value:
        ...         case str():
        ...             print(f"String: {value!r}")
        ...         case int():
        ...             print(f"Integer: {value!r}")
        ...         case _:
        ...             msg = "value is not a valid 'str | int'"
        ...             raise construct_type_error(value, msg)
        ...
        >>> fake_int = cast("int", 3.14)
        >>> handle_str_or_int(fake_int)
        Traceback (most recent call last):
          ...
        TypeError: value is not a valid 'str | int'
    """
    return TypeError(*args)
