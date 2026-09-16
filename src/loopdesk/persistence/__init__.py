"""Persistence layer: schema migration + related primitives.

Public entry point is :func:`loopdesk.persistence.migrator.apply_pending`.
"""

from loopdesk.persistence.migrator import apply_pending

__all__ = ["apply_pending"]
