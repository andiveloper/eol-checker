"""Data providers for dependency findings."""

from eol_checker.providers.base import (
    Provider,
    ProviderRegistry,
    aggregate_findings,
    default_providers,
)

__all__ = [
    "Provider",
    "ProviderRegistry",
    "aggregate_findings",
    "default_providers",
]
