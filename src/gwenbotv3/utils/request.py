"""Houses a custom request function for requests.

Use the request function for any and all requests
instead of using requests.get directly.
"""

import logging
import random
import time

import requests

from gwenbotv3.exceptions import FailedRequestError


def request(url: str, headers: dict[str, str] | None = None) -> requests.Response:
    """Use for all GET requests.

    Args:
        url (str): url
        header (Dict[str, str], optional): Headers, if applicable.
        Defaults to {'User-Agent': 'Mozilla/5.0'}.

    Returns:
        Response: request Response.
    """
    if headers is None:
        headers = {
            "User-Agent": ("Mozilla/5.0 (Win64; x64)"),
            "Accept-Language": "en-GB,en;q=0.9",
            "Referer": "https://u.gg/",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Upgrade-Insecure-Requests": "1",
        }
    logger = logging.getLogger(__name__)
    logger.debug("Requesting url %s with headers %s", url, headers)

    session = requests.Session()
    session.headers.update(headers)

    try:
        response = session.get(url=url, headers=headers, timeout=10)
    except requests.exceptions.Timeout as exc:
        raise FailedRequestError(url=url, headers=headers, reason="Timeout") from exc

    if response.status_code == 403:
        for _ in range(3):
            response = session.get(url=url, headers=headers, timeout=10)
            if response.ok:
                break
            time.sleep(random.uniform(2, 5))

    while response.status_code == 429:
        time.sleep(int(response.headers.get("Retry-After", 1)))
        try:
            response = session.get(url=url, headers=headers, timeout=10)
        except requests.exceptions.Timeout as exc:
            raise FailedRequestError(
                url=url, headers=headers, reason="Timeout"
            ) from exc

    if not response.ok:
        raise FailedRequestError(
            url=url,
            headers=headers,
            reason="Response not OK",
            status_code=response.status_code,
            status_headers=response.headers,
        )

    return response
