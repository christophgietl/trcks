"""Recent features from `typing`.

Imported from `typing_extensions` if necessary in older Python versions.
This helps to avoid `sys.version_info` checks in the codebase.
"""

import sys

if sys.version_info >= (3, 13):  # pragma: no cover
    from typing import TypeVar  # Argument "default" has been added in Python 3.13.
else:  # pragma: no cover
    from typing_extensions import TypeVar

if sys.version_info >= (3, 12):  # pragma: no cover
    from typing import override
else:  # pragma: no cover
    from typing_extensions import override

if sys.version_info >= (3, 11):  # pragma: no cover
    from typing import Never, assert_never
else:  # pragma: no cover
    from typing_extensions import Never, assert_never

__all__ = [
    "Never",
    "TypeVar",
    "assert_never",
    "override",
]
__docformat__ = "google"
