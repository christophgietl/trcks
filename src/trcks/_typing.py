"""Recent features from `typing`.

Imported from `typing_extensions` if necessary in older Python versions.
This helps to avoid `sys.version_info` checks in the codebase.
"""

import sys

if sys.version_info >= (3, 11):  # pragma: no cover
    from typing import Never, TypeAlias, assert_never
else:
    from typing_extensions import Never, TypeAlias, assert_never

if sys.version_info >= (3, 13):  # pragma: no cover
    from typing import assert_type
else:
    from typing_extensions import assert_type

__all__ = [
    "Never",
    "TypeAlias",
    "assert_never",
    "assert_type",
]
__docformat__ = "google"
