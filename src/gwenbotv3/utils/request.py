"""Houses a custom request function for requests.

Use the request function for any and all requests.
"""

import asyncio
import logging
import random

from aiohttp import ClientError, ClientResponse, ClientSession
from multidict import CIMultiDictProxy

from gwenbotv3.exceptions import FailedRequestError

logger = logging.getLogger(__name__)


async def _retry_after(response: ClientResponse, url: str) -> None:
    """Checks for retry after and async sleeps if one is found"""
    retry_after_raw = response.headers.get("Retry-After", "1")

    try:
        retry_after = int(retry_after_raw)
    except ValueError:
        logger.debug(
            "Retry-After was not an int, got %s on url %s", retry_after_raw, url
        )
        await asyncio.sleep(1)
        return

    if retry_after > 30:
        logger.warning("Retry-After > 30, got %i on url %s", retry_after, url)
        return

    logger.debug(
        "Hit retry-after for %i seconds in request for url %s", retry_after, url
    )
    await asyncio.sleep(retry_after)


async def _handle_response(
    response: ClientResponse,
    url: str,
    headers: dict[str, str],
    attempt: int,
) -> bytes | None:
    """Checks if response is OK"""
    status = response.status

    if status == 429:
        await _retry_after(response, url)
        return None

    if status == 403 and attempt < 3:
        await asyncio.sleep(random.uniform(2, 5))
        return None

    if not response.ok:
        raise FailedRequestError(
            url=url,
            headers=headers,
            reason="Response not OK",
            status_code=status,
            status_headers=response.headers,
        )

    return await response.read()


async def _attempt(
    session: ClientSession,
    url: str,
    headers: dict[str, str],
    params: dict[str, str] | None,
    attempt: int,
) -> tuple[bytes | None, int | None, CIMultiDictProxy[str]]:
    """Performs a single connection attempt.

    For parametres see request.

    Returns
    -------
    tuple[bytes | None, int | None, object]
        result, status, headers
    """
    try:
        async with session.get(url, headers=headers, params=params) as response:
            result = await _handle_response(response, url, headers, attempt)
            return result, response.status, response.headers

    except TimeoutError as exc:
        raise FailedRequestError(url=url, headers=headers, reason="Timeout") from exc
    except ClientError as exc:
        raise FailedRequestError(
            url=url, headers=headers, reason="Client error"
        ) from exc


async def request(
    session: ClientSession,
    url: str,
    *,
    headers: dict[str, str] | None = None,
    params: dict[str, str] | None = None,
) -> bytes:
    """Request content of a url call.

    Parameters
    ----------
    session : ClientSession
        aiohttp session.
    url : str
        url to request.
    headers : dict[str, str] | None, optional
        Optional headers. Will use a header preset if None are given. by default None
    params : dict[str, str] | None, optional
        Additional parametres for the request call. by default None

    Returns
    -------
    bytes
        Result of the call.

    Raises
    ------
    FailedRequestError
        If the request fails.
    """
    if headers is None:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:152.0)"
                " Gecko/20100101 Firefox/152.0"
            ),
            "Accept-Language": "en-GB,en;q=0.9",
            "Referer": "https://lolalytics.com/",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Upgrade-Insecure-Requests": "1",
        }

    status = None
    resp_headers = None

    for attempt in range(4):
        result, status, resp_headers = await _attempt(
            session=session, url=url, headers=headers, params=params, attempt=attempt
        )
        if result is not None:
            return result

    raise FailedRequestError(
        url=url,
        headers=headers,
        reason="Response not OK",
        status_code=status,
        status_headers=resp_headers,
    )
