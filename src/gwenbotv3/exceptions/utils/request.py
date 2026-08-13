"""Exceptions for request module."""

import logging
from typing import Any

logger = logging.getLogger(__name__)


class FailedRequestError(Exception):
    """
    Raise if a request has failed for any reason
    not handled by the request function."""

    def __init__(self, **kwargs: Any) -> None:
        logger.error("Request failed with %s", kwargs)
        super().__init__(f"Request failed with {kwargs=}")
