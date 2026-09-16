"""Web search abstraction layer."""

from loopdesk.search.registry import get_provider, register_provider
from loopdesk.search.types import (
    SearchProvider,
    SearchProviderError,
    SearchProviderSpec,
    SearchRequest,
    SearchResult,
)

__all__ = [
    "SearchResult",
    "SearchRequest",
    "SearchProviderSpec",
    "SearchProviderError",
    "SearchProvider",
    "get_provider",
    "register_provider",
]
