from typing import Generic

from trcks._typing import TypeVar, override

__docformat__ = "google"

_T_co = TypeVar("_T_co", covariant=True)


class BaseWrapper(Generic[_T_co]):
    """Base class for all wrappers in the [trcks.oop][] package.

    Attributes:
        __slots__: Attribute names to be used.
    """

    __slots__: tuple[str, ...] = ("_core",)

    def __init__(self, core: _T_co) -> None:
        """Construct wrapper.

        Args:
            core: The value to be wrapped.
        """
        super().__init__()
        self._core: _T_co = core

    @override
    def __repr__(self) -> str:
        """Return a string representation of the wrapper."""
        return f"{self.__class__.__name__}(core={self._core!r})"

    @property
    def core(self) -> _T_co:
        """The wrapped value."""
        return self._core
