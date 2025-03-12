from __future__ import annotations

import dataclasses
from typing import Generic

from trcks._typing import TypeVar

__docformat__ = "google"

_T_co = TypeVar("_T_co", covariant=True)


@dataclasses.dataclass(frozen=True)
class BaseWrapper(Generic[_T_co]):
    """Base class for all wrappers in the `trcks.oop` module.

    Attributes:
        core: The wrapped object.

    Args:
        core: The object to be wrapped.
    """

    core: _T_co
