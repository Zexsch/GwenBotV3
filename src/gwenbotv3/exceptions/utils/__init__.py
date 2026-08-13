"""Exceptions for utils."""

from .confirmation_button_exceptions import NoViewError
from .request_exceptions import FailedRequestError

__all__ = ["FailedRequestError", "NoViewError"]
