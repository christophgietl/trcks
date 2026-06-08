"""Exception classes for [trcks][]."""

from collections.abc import Sized

__docformat__ = "google"


class TrcksTypeError(TypeError):
    """Raised when [trcks][] functions are called with an argument of wrong type.

    Contains information about the offending object.

    Attributes:
        offending_object_class: Class of the object that caused the error.
        offending_object_length: Length of the object that caused the error.
        expected_type_name: Name of the expected type.

    Example:
        Offending object has a length:

        >>> obj = ("not_a_success", "msg")
        >>> err = TrcksTypeError(obj, "Result")
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
        >>> err = TrcksTypeError(obj, "Result")
        >>> str(err)
        "object of type 'int' is not a valid 'Result'"
        >>> err.offending_object_class
        <class 'int'>
        >>> err.offending_object_length is None
        True
        >>> err.expected_type_name
        'Result'
    """

    __slots__ = (
        "expected_type_name",
        "offending_object_class",
        "offending_object_length",
    )

    def __init__(
        self,
        offending_object: object,
        expected_type_name: str,
    ) -> None:
        """Initialize exception.

        Args:
            offending_object: Object that caused the error.
            expected_type_name: Name of the expected type.
        """
        self.offending_object_class: type = type(offending_object)
        self.offending_object_length: int | None = (
            len(offending_object) if isinstance(offending_object, Sized) else None
        )
        self.expected_type_name: str = expected_type_name

        prefix = f"object of type '{self.offending_object_class.__name__}' "
        if self.offending_object_length is None:
            infix = ""
        else:
            infix = f"and length {self.offending_object_length} "
        suffix = f"is not a valid '{self.expected_type_name}'"

        super().__init__(f"{prefix}{infix}{suffix}")
