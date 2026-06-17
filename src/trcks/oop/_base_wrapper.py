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

    Note:
        Instances of this class (and its synchronous subclasses) are unhashable
        because `__eq__` is defined.
        Awaitable subclasses such as [trcks.oop.BaseAwaitableWrapper][]
        restore identity-based equality and remain hashable.

    Example:
        >>> from trcks.oop import BaseWrapper
        >>> wrapped_integer: BaseWrapper[int] = BaseWrapper(core=42)
        >>> wrapped_integer
        BaseWrapper(core=42)
        >>> wrapped_integer.core
        42
    """

    __hash__ = None  # type: ignore[assignment]  # pyright: ignore[reportAssignmentType]  # pyrefly: ignore[implicit-any-attribute]  # Explicitly unhashable because __eq__ is defined.

    __slots__: tuple[str, ...] = ("_core",)

    @override
    def __eq__(self, other: object) -> bool:
        """Check equality based on the wrapped value and the wrapper class.

        Two wrappers are equal if and only if they are instances of the same class
        and their wrapped values are equal.

        Args:
            other: The object to compare with.

        Returns:
            `True` if `other` is an instance of the same class and has an equal
            wrapped value; `False` if `other` is an instance of the same class
            but has a different wrapped value;
            `NotImplemented` for any other type.

        Example:
            >>> from trcks.oop import BaseWrapper
            >>> BaseWrapper(core=42) == BaseWrapper(core=42)
            True
            >>> BaseWrapper(core=42) == BaseWrapper(core=0)
            False
            >>> BaseWrapper(core=42).__eq__(42)
            NotImplemented
        """
        if not isinstance(other, BaseWrapper) or type(other) is not type(self):  # pyright: ignore[reportUnknownArgumentType]
            return NotImplemented
        return bool(self._core == other._core)  # pyright: ignore[reportUnknownArgumentType, reportUnknownMemberType]

    def __init__(self, core: _T_co) -> None:
        """Initialize the wrapper.

        Args:
            core: The value to be wrapped.
        """
        super().__init__()
        self._core: _T_co = core

    @override
    def __repr__(self) -> str:
        """Return a textual representation of the wrapper.

        Returns:
            The textual representation of the wrapper.
        """
        return f"{self.__class__.__name__}(core={self._core!r})"

    @property
    def core(self) -> _T_co:
        """The wrapped value."""
        return self._core
