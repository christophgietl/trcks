from typing import Final, Generic

from trcks._typing import Never, TypeVar, override
from trcks.exceptions import TrcksFrozenInstanceError

__docformat__ = "google"

_T_co = TypeVar("_T_co", covariant=True)


class BaseWrapper(Generic[_T_co]):
    """Base class for all wrappers in the [trcks.oop][] package.

    Attributes:
        core: The wrapped value.

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

        Equality depends on the class and on the wrapped value:

            >>> from trcks.oop import BaseWrapper
            >>> BaseWrapper(core=42) == BaseWrapper(core=42)
            True
            >>> BaseWrapper(core=42) == BaseWrapper(core=0)
            False
            >>> class SubWrapper(BaseWrapper[int]):
            ...     pass
            >>> SubWrapper(core=42) == BaseWrapper(core=42)
            False
            >>> BaseWrapper(core=42) == SubWrapper(core=42)
            False

        Same class and same wrapped value implies same hash:

            >>> from trcks.oop import BaseWrapper
            >>> hash(BaseWrapper(core=42)) == hash(BaseWrapper(core=42))
            True
            >>> class SubWrapper(BaseWrapper[int]):
            ...     pass
            >>> hash(SubWrapper(core=42)) == hash(SubWrapper(core=42))
            True

        Unhashable values lead to unhashable wrappers:

            >>> from trcks.oop import BaseWrapper
            >>> hash(BaseWrapper(core=[1, 2, 3]))
            Traceback (most recent call last):
                ...
            TypeError: unhashable type: 'list'

        Wrappers are immutable:

            >>> from trcks.oop import BaseWrapper
            >>> wrapper = BaseWrapper(core=42)
            >>> wrapper.core = 100
            Traceback (most recent call last):
                ...
            trcks.exceptions.TrcksFrozenInstanceError: cannot assign to attribute 'core'
            >>> del wrapper.core
            Traceback (most recent call last):
                ...
            trcks.exceptions.TrcksFrozenInstanceError: cannot delete attribute 'core'
    """

    # Data classes do not play nicely with covariant type variables in Python 3.13+
    # (see https://github.com/microsoft/pyright/discussions/11012 and https://github.com/python/mypy/issues/17623).
    # Therefore, we need to implement the following dunder methods and attributes
    # manually:

    __slots__: tuple[str, ...] = ("core",)

    @override
    def __delattr__(self, name: str) -> Never:
        """Prevent attribute deletion.

        Raises:
            TrcksFrozenInstanceError: Always.
        """
        msg = f"cannot delete attribute {name!r}"
        raise TrcksFrozenInstanceError(msg, name=name, obj=self)

    @override
    def __eq__(self, other: object) -> bool:
        """Check if this wrapper is equal to another object.

        Args:
            other: The object to compare with.

        Returns:
            NotImplemented if the classes differ.
                False if the wrapped values differ.
                True otherwise.
        """
        if type(other) is type(self):
            return other.core == self.core
        return NotImplemented

    @override
    def __hash__(self) -> int:
        """Hash the wrapper.

        Returns:
            The hash of the wrapper.
        """
        return hash((type(self), self.core))

    def __init__(self, core: _T_co) -> None:
        """Initialize the wrapper.

        Args:
            core: The value to be wrapped.
        """
        super().__init__()
        self.core: Final[_T_co] = core

    @override
    def __repr__(self) -> str:
        """Represent the wrapper textually.

        Returns:
            The textual representation of the wrapper.
        """
        return f"{self.__class__.__name__}(core={self.core!r})"

    @override
    def __setattr__(self, name: str, value: object) -> None:
        """Set attribute during initialization.

        Args:
            name: The name of the attribute.
            value: The value to set.

        Raises:
            TrcksFrozenInstanceError: If the attribute already exists.
        """
        try:
            self.__getattribute__(name)
        except AttributeError:
            pass  # Attribute does not exist yet.
        else:
            msg = f"cannot assign to attribute {name!r}"
            raise TrcksFrozenInstanceError(msg, name=name, obj=self)

        # Raises AttributeError if name is not in __slots__:
        super().__setattr__(name, value)
