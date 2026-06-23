"""Exception classes for [trcks][]."""

from __future__ import annotations

from collections.abc import Sized
from dataclasses import dataclass
from typing import TYPE_CHECKING, Final

if TYPE_CHECKING:
    from trcks._typing import Self

__docformat__ = "google"


@dataclass(eq=False, init=False, repr=False, slots=True)
class TrcksError(Exception):
    """Base class for all exceptions raised by [trcks][]."""


@dataclass(eq=False, repr=False, slots=True)
class TrcksTypeError(TrcksError, TypeError):
    """Raised when [trcks][] functions are called with an argument of wrong type.

    Attributes:
        offending_object_class: Class of the object that caused the error.
        offending_object_length: Length of the object that caused the error.
        expected_type_name: Name of the expected type.

    Example:
        >>> err = TrcksTypeError(int, None, "Pipeline")
        >>> err
        TrcksTypeError("object of type 'int' is not a valid 'Pipeline'")
        >>> err.offending_object_class
        <class 'int'>
        >>> err.offending_object_length is None
        True
        >>> err.expected_type_name
        'Pipeline'
    """

    offending_object_class: Final[type]
    offending_object_length: Final[int | None]
    expected_type_name: Final[str]

    def __post_init__(self) -> None:
        """Post-init processing for [dataclasses.dataclass][]."""
        prefix = f"object of type '{self.offending_object_class.__name__}' "
        if self.offending_object_length is None:
            infix = ""
        else:
            infix = f"and length {self.offending_object_length} "
        suffix = f"is not a valid '{self.expected_type_name}'"

        super(TrcksTypeError, self).__init__(f"{prefix}{infix}{suffix}")

    @classmethod
    def construct_from_offending_object(
        cls,
        offending_object: object,
        expected_type_name: str,
    ) -> Self:
        """Create error from an offending object and the expected type.

        Args:
            offending_object: Object that caused the error.
            expected_type_name: Name of the expected type.

        Returns:
            Information about the offending object and the expected type.

        Example:
            Offending object has a length:

            >>> obj = ("not_a_success", "msg")
            >>> err = TrcksTypeError.construct_from_offending_object(obj, "Result")
            >>> str(err)
            "object of type 'tuple' and length 2 is not a valid 'Result'"
            >>> err.offending_object_class
            <class 'tuple'>
            >>> err.offending_object_length
            2
            >>> err.expected_type_name
            'Result'

            Offending object does not have a length:

            >>> obj = 42
            >>> err = TrcksTypeError.construct_from_offending_object(obj, "Result")
            >>> str(err)
            "object of type 'int' is not a valid 'Result'"
            >>> err.offending_object_class
            <class 'int'>
            >>> err.offending_object_length is None
            True
            >>> err.expected_type_name
            'Result'
        """
        offending_object_class = type(offending_object)
        if isinstance(offending_object, Sized):
            offending_object_length = len(offending_object)
        else:
            offending_object_length = None
        return cls(
            offending_object_class=offending_object_class,
            offending_object_length=offending_object_length,
            expected_type_name=expected_type_name,
        )
