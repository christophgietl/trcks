"""Functions for the identity monad.

Provides utilities for functional composition of synchronous functions.
"""

from __future__ import annotations

from trcks.fp._monads.identity import tap

__all__ = ["tap"]
__docformat__ = "google"

# Re-assign __module__ to match the facade module name for test compatibility
tap.__module__ = __name__
