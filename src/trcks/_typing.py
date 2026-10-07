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

__all__ = [
    "TypeVar",
    "deprecated",
]
__docformat__ = "google"
