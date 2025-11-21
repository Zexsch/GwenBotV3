import time
import requests
from typing import Dict

from logger import SingletonLogger

logger = SingletonLogger().get_logger()

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
        logger.warning(f"Timeout during request url: {url} with headers {headers}")
    
    while response.status_code == 429: # type: ignore
        time.sleep(int(response.headers.get("Retry-After", 1))) # type: ignore
        try:
            response = requests.get(url=url, headers=headers, timeout=10)
        except requests.exceptions.Timeout:
            logger.warning(f"Timeout during request url: {url} with headers {headers}")
            response.raise_for_status() # type: ignore
        
    if not response.ok: # type: ignore
        logger.warning(f"Response not OK with url: {url} with headers {headers}")
        response.raise_for_status() # type: ignore
    
    return response # type: ignore
    