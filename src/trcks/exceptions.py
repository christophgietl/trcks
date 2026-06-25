"""Exception classes for [trcks][]."""

from dataclasses import dataclass

__docformat__ = "google"


@dataclass(eq=False, init=False, repr=False, slots=True)
class TrcksError(Exception):
    """Base class for all exceptions raised by [trcks][]."""


@dataclass(eq=False, init=False, repr=False, slots=True)
class TrcksFrozenInstanceError(TrcksError, AttributeError):
    """Raised when trying to modify an instance of a frozen [trcks][] class.

    Example:
        >>> err = TrcksFrozenInstanceError(
        ...     "cannot assign to attribute 'x'", name="x", obj=42
        ... )
        >>> err
        TrcksFrozenInstanceError("cannot assign to attribute 'x'")
        >>> err.name
        'x'
        >>> err.obj
        42
    """
