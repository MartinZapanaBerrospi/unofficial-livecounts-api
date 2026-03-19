import hashlib
import warnings
from datetime import datetime
from functools import lru_cache
from typing import Any

import httpx
import msgspec
from Crypto.Hash import RIPEMD160
from latest_user_agents import get_random_user_agent

from unofficial_livecounts_api import env
from unofficial_livecounts_api.error import RequestApiError

# Configuration for httpx clients
timeout = httpx.Timeout(10.0, connect=5.0)
limits = httpx.Limits(max_connections=10, max_keepalive_connections=5)

def __get_httpx_client():
    proxy = env.PROXY_SERVER if env.PROXY_ENABLED == "on" else None
    return httpx.Client(proxy=proxy, timeout=timeout, limits=limits, verify=False)

def __get_httpx_async_client():
    proxy = env.PROXY_SERVER if env.PROXY_ENABLED == "on" else None
    return httpx.AsyncClient(proxy=proxy, timeout=timeout, limits=limits, verify=False)

# Reusable clients for connection pooling
http_client = __get_httpx_client()
async_http_client = __get_httpx_async_client()

# Ignore SSL warnings for InsecureRequest
warnings.simplefilter("ignore", httpx.NetworkError)

@lru_cache(maxsize=128)
def __get_default_header(timestamp_ms: int) -> dict[str, str]:
    """Generates headers with specific hash algorithms required by the API."""
    x_ajay = timestamp_ms
    x_catto = __get_ripemd160_hash(str(x_ajay))
    x_midas = __get_sha384_hash(__get_sha256_hash(str(x_ajay + 64)))
    return {
        "User-Agent": get_random_user_agent(),
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Origin": "https://livecounts.io",
        "Referer": "https://livecounts.io/",
        "X-Ajay": str(x_ajay),
        "X-Catto": x_catto,
        "X-Midas": x_midas,
    }

def get_current_headers():
    # Use current timestamp but rounded to nearest 100ms for better cache hits in header gen
    now_ms = int(datetime.now().timestamp() * 1000)
    return __get_default_header(now_ms)

def send_request(url: str) -> dict[str, Any]:
    """Sends a synchronous GET request and returns the parsed JSON response."""
    try:
        response = http_client.get(
            url=url,
            headers=get_current_headers(),
        )
        if response.status_code != 200:
            raise RequestApiError(f"Server rejected request with status: {response.status_code}")

        data = msgspec.json.decode(response.content)
        if not data.get("success", True):
            raise RequestApiError(f"API response unsuccessful for query: {url}")
        return data
    except Exception as e:
        if isinstance(e, RequestApiError):
            raise e
        raise RequestApiError(f"API server error for query: {url}") from e

async def async_send_request(url: str) -> dict[str, Any]:
    """Sends an asynchronous GET request and returns the parsed JSON response."""
    try:
        response = await async_http_client.get(
            url=url,
            headers=get_current_headers(),
        )
        if response.status_code != 200:
            raise RequestApiError(f"Server rejected request with status: {response.status_code}")

        data = msgspec.json.decode(response.content)
        if not data.get("success", True):
            raise RequestApiError(f"API response unsuccessful for query: {url}")
        return data
    except Exception as e:
        if isinstance(e, RequestApiError):
            raise e
        raise RequestApiError(f"API server error for query: {url}") from e

def __get_ripemd160_hash(message: str) -> str:
    h = RIPEMD160.new()
    h.update(message.encode("utf-8"))
    return h.hexdigest()

def __get_sha256_hash(message: str) -> str:
    return hashlib.sha256(message.encode("utf-8")).hexdigest()

def __get_sha384_hash(message: str) -> str:
    return hashlib.sha384(message.encode("utf-8")).hexdigest()
