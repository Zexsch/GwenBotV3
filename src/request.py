import time
import requests
from typing import Dict

from logger import SingletonLogger

logger = SingletonLogger().get_logger()

class FailedRequest(Exception):
    def __init__(self, **kwargs) -> None:
        logger.error(f"Request failed with {kwargs=}")
        super().__init__(f"Request failed with {kwargs=}")

def request(url: str, headers: Dict[str, str] = {'User-Agent': 'Mozilla/5.0'}) -> requests.Response:
    """Use for all GET requests.

    Args:
        url (str): url
        header (Dict[str, str], optional): Headers, if applicable. Defaults to {'User-Agent': 'Mozilla/5.0'}.

    Returns:
        Response: request Response.
    """
    logger.debug(f"Requesting url {url} with headers {headers}")
    
    try:
        response = requests.get(url=url, headers=headers, timeout=10)
    except requests.exceptions.Timeout:
        raise FailedRequest(url=url, headers=headers, reason="Timeout")
    
    while response.status_code == 429:
        time.sleep(int(response.headers.get("Retry-After", 1)))
        try:
            response = requests.get(url=url, headers=headers, timeout=10)
        except requests.exceptions.Timeout:
            raise FailedRequest(url=url, headers=headers, reason="Timeout")
        
    if not response.ok:
        raise FailedRequest(url=url, headers=headers, reason="Response not OK", status_code=response.status_code)
    
    return response