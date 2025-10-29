# Custom exceptions for pynigeria.

from __future__ import annotations


class PyNigeriaError(Exception):
    """Base exception for all pynigeria errors."""

    pass


class DataLoadError(PyNigeriaError):
    """Raised when data files cannot be loaded or parsed."""

    pass


class DataIntegrityError(PyNigeriaError):
    """Raised when data validation fails."""

    pass


class NotFoundError(PyNigeriaError):
    """Raised when a requested resource is not found."""

    pass


