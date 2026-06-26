"""Recent features from `typing` and `warnings`.

Imported from `typing_extensions` if necessary in older Python versions.
This helps to avoid `sys.version_info` checks in the codebase.
"""

import sys

if sys.version_info >= (3, 13):  # pragma: no cover
    from typing import TypeVar  # Argument "default" has been added in Python 3.13.
    from warnings import deprecated
else:  # pragma: no cover
    from typing_extensions import TypeVar, deprecated

if sys.version_info >= (3, 12):  # pragma: no cover
    from typing import override
else:  # pragma: no cover
    from typing_extensions import override

if sys.version_info >= (3, 11):  # pragma: no cover
    from typing import Never, Self, assert_type
else:  # pragma: no cover
    from typing_extensions import Never, Self, assert_type

__all__ = [
    "Never",
    "Self",
    "TypeVar",
    "assert_type",
    "deprecated",
    "override",
]
__docformat__ = "google"
