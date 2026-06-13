from abc import ABC, abstractmethod
from typing import Generic

from trcks._typing import TypeVar, override

__docformat__ = "google"

_T_co = TypeVar("_T_co", covariant=True)


class AbstractWrapper(ABC, Generic[_T_co]):
    """Abstract base class for all wrappers in the [trcks.oop][] package.

    Note:
        This class is abstract and cannot be instantiated directly.
        If you want to wrap a value, please use one of the concrete subclasses instead,
        such as [trcks.oop.Wrapper][].

    Example:
        >>> from trcks.oop import AbstractWrapper
        >>> AbstractWrapper(42)
        Traceback (most recent call last):
          ...
        TypeError: Can't instantiate abstract class AbstractWrapper ...
    """

    __slots__: tuple[str, ...] = ("_core",)

    def __init__(self, core: _T_co) -> None:
        """Wrap a value.

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

    @abstractmethod
    def _abc_dummy(self) -> None:
        """Make this class abstract."""

    @property
    def core(self) -> _T_co:
        """The wrapped value."""
        return self._core
