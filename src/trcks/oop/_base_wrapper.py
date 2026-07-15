from dataclasses import dataclass
from typing import Generic

from trcks._typing import TypeVar

__docformat__ = "google"

_T_co = TypeVar("_T_co", covariant=True)


@dataclass(frozen=True, slots=True)
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
            >>> wrapped_integer = BaseWrapper(core=42)
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
            ...     def __init__(self, core: int, metadata: str) -> None:
            ...         super().__init__(core)
            ...         object.__setattr__(self, "metadata", metadata)
            >>> SubWrapper(core=42, metadata="x") == BaseWrapper(core=42)
            False
            >>> BaseWrapper(core=42) == SubWrapper(core=42, metadata="x")
            False
            >>> SubWrapper(core=42, metadata="x") == SubWrapper(core=42, metadata="y")
            True

        Same class and same wrapped value implies same hash:

            >>> from trcks.oop import BaseWrapper
            >>> hash(BaseWrapper(core=42)) == hash(BaseWrapper(core=42))
            True
            >>> class SubWrapper(BaseWrapper[int]):
            ...     def __init__(self, core: int, metadata: str) -> None:
            ...         super().__init__(core)
            ...         object.__setattr__(self, "metadata", metadata)
            >>> hash(
            ...     SubWrapper(core=42, metadata="x")
            ... ) == hash(SubWrapper(core=42, metadata="y"))
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
            dataclasses.FrozenInstanceError: cannot assign to field 'core'
            >>> del wrapper.core
            Traceback (most recent call last):
                ...
            dataclasses.FrozenInstanceError: cannot delete field 'core'
    """

    core: _T_co  # type: ignore[misc, unused-ignore]    # see https://github.com/python/mypy/issues/21736
