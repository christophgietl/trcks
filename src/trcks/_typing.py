"""Recent features from `typing`.

Imported from `typing_extensions` if necessary in older Python versions.
This helps to avoid `sys.version_info` checks in the codebase.
"""

import sys

if sys.version_info >= (3, 13):  # pragma: no cover
    from typing import TypeVar  # Argument "default" has been added in Python 3.13.
else:
    from typing_extensions import TypeVar

if sys.version_info >= (3, 12):  # pragma: no cover
    from typing import override
else:
    from typing_extensions import override

if sys.version_info >= (3, 11):  # pragma: no cover
    from typing import Never, TypeAlias, assert_never
else:
    from typing_extensions import Never, TypeAlias, assert_never

__all__ = [
    "Never",
    "TypeAlias",
    "TypeVar",
    "assert_never",
    "override",
]
__docformat__ = "google"
