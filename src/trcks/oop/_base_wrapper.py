from typing import Generic

from trcks._typing import TypeVar, override

__docformat__ = "google"

_T_co = TypeVar("_T_co", covariant=True)


class BaseWrapper(Generic[_T_co]):
    """Base class for all wrappers in the [trcks.oop][] package.

    Note:
        This class is not particularly useful by itself.
        If you want to wrap and process a value,
        please consider using one of its subclasses,
        such as [trcks.oop.Wrapper][].

    Example:
        Wrapping and unwrapping an integer:

            >>> from trcks.oop import BaseWrapper
            >>> wrapped_integer = BaseWrapper[int](core=42)
            >>> wrapped_integer
            BaseWrapper(core=42)
            >>> unwrapped_integer = wrapped_integer.core
            >>> unwrapped_integer
            42

        Equality depends on the wrapper class and on the wrapped value:

            >>> from trcks.oop import BaseWrapper
            >>> BaseWrapper(core=42) == BaseWrapper(core=42)
            True
            >>> BaseWrapper(core=42) == BaseWrapper(core=0)
            False
            >>> class SubWrapper(BaseWrapper[int]):
            ...     pass
            >>> SubWrapper(core=42) == BaseWrapper(core=42)
            False

        Same wrapper class and same wrapped value implies same hash:

            >>> from trcks.oop import BaseWrapper
            >>> hash(BaseWrapper(core=42)) == hash(BaseWrapper(core=42))
            True

        Unhashable values result in unhashable wrappers:

            >>> hash(BaseWrapper(core=[1, 2, 3]))
            Traceback (most recent call last):
                ...
            TypeError: unhashable type: 'list'
    """

    __slots__: tuple[str, ...] = ("_core",)

    @override
    def __eq__(self, other: object) -> bool:
        """Check if this wrapper is equal to another object.

        Args:
            other: The object to compare with.

        Returns:
            True if the classes are identical _and_ the wrapped values are equal. False otherwise.
        """
        return type(other) is type(self) and other._core == self._core

    @override
    def __hash__(self) -> int:
        """Hash the wrapper.

        Returns:
            The hash of the wrapper.
        """
        return hash((type(self), self._core))

    def __init__(self, core: _T_co) -> None:
        """Initialize the wrapper.

        Args:
            core: The value to be wrapped.
        """
        super().__init__()
        self._core: _T_co = core

    @override
    def __repr__(self) -> str:
        """Represent the wrapper textually.

        Returns:
            The textual representation of the wrapper.
        """
        return f"{self.__class__.__name__}(core={self._core!r})"

    @property
    def core(self) -> _T_co:
        """The wrapped value."""
        return self._core
