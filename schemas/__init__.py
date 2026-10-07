"""Shared error type for offline record and repository validation."""


class ValidationError(ValueError):
    """An input fails an explicit, versioned validation contract."""
