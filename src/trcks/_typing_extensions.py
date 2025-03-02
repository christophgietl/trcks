"""Imports objects from typing_extensions if necessary, otherwise from typing.

This helps to avoid sys.version_info checks in the codebase.
"""

import sys

if sys.version_info >= (3, 11):  # pragma: no cover
    from typing import Never, TypeAlias
else:
    from typing_extensions import Never, TypeAlias

if sys.version_info >= (3, 13):  # pragma: no cover
    from typing import (
        TypeVar,  # typing.TypeVar does not have the attribute "default" before 3.13.
        assert_type,
    )
else:
    from typing_extensions import (
        TypeVar,
        assert_type,
    )

__all__ = [
    "Never",
    "TypeAlias",
    "TypeVar",
    "assert_type",
]
__docformat__ = "google"
