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
        >>> from trcks.oop import BaseWrapper
        >>> wrapped_integer = BaseWrapper[int](core=42)
        >>> wrapped_integer
        BaseWrapper(core=42)
        >>> wrapped_integer.core
        42
    """

    __slots__: tuple[str, ...] = ("_core",)

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
