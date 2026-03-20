import os
import re
import hashlib
import warnings
import asyncio
from datetime import datetime
from functools import lru_cache
from typing import Any
from urllib.parse import quote

import httpx
import msgspec
import validators
from Crypto.Hash import RIPEMD160
from latest_user_agents import get_random_user_agent
from dotenv import load_dotenv

# --- Environment Configuration ---
load_dotenv()

PROXY_ENABLED = os.getenv("PROXY_ENABLED", "off")
PROXY_SERVER = os.getenv("PROXY_SERVER", None)

TIKTOK_USER_SEARCH_API = os.getenv("TIKTOK_USER_SEARCH_API", "https://tiktok-api.tokcounter.com/user/search").removesuffix("/")
TIKTOK_USER_STATS_API = os.getenv("TIKTOK_USER_STATS_API", "https://tiktok-api.tokcounter.com/user/stats").removesuffix("/")
TIKTOK_VIDEO_SEARCH_API = os.getenv("TIKTOK_VIDEO_SEARCH_API", "https://tiktok-api.tokcounter.com/video/data").removesuffix("/")
TIKTOK_VIDEO_STATS_API = os.getenv("TIKTOK_VIDEO_STATS_API", "https://tiktok-api.tokcounter.com/video/stats").removesuffix("/")

YOUTUBE_CHANNEL_SEARCH_API = os.getenv("YOUTUBE_CHANNEL_SEARCH_API", "https://api.livecounts.io/youtube-live-subscriber-counter/search").removesuffix("/")
YOUTUBE_VIDEO_SEARCH_API = os.getenv("YOUTUBE_VIDEO_SEARCH_API", "https://api.livecounts.io/youtube-live-view-counter/search").removesuffix("/")
YOUTUBE_CHANNEL_STATS_API = os.getenv("YOUTUBE_CHANNEL_STATS_API", "https://api.livecounts.io/youtube-live-subscriber-counter/stats").removesuffix("/")
YOUTUBE_VIDEO_STATS_API = os.getenv("YOUTUBE_VIDEO_STATS_API", "https://api.livecounts.io/youtube-live-view-counter/stats").removesuffix("/")

TWITTER_USER_SEARCH_API = os.getenv("TWITTER_USER_SEARCH_API", "https://api.livecounts.io/twitter-live-follower-counter/search").removesuffix("/")
TWITTER_USER_STATS_API = os.getenv("TWITTER_USER_STATS_API", "https://api.livecounts.io/twitter-live-follower-counter/stats").removesuffix("/")

# --- Errors ---
class RequestApiError(Exception):
    def __init__(self, message: str):
        super().__init__(message)

# --- Utilities & Networking ---
timeout = httpx.Timeout(15.0, connect=8.0)
limits = httpx.Limits(max_connections=20, max_keepalive_connections=10)

def __get_httpx_client():
    proxy = PROXY_SERVER if PROXY_ENABLED == "on" else None
    return httpx.Client(proxy=proxy, timeout=timeout, limits=limits, verify=False)

http_client = __get_httpx_client()
warnings.simplefilter("ignore", httpx.NetworkError)

@lru_cache(maxsize=128)
def __get_default_header(timestamp_ms: int, is_tiktok: bool = False) -> dict[str, str]:
    # Corrected Signatures based on Live Audit
    ts_str = str(timestamp_ms)
    
    # X-Ajay: SHA-1 of the timestamp (Livecounts standard)
    x_ajay = hashlib.sha1(ts_str.encode()).hexdigest()
    
    # X-Midas: Derived from timestamp
    x_midas_base = hashlib.sha256(ts_str.encode()).hexdigest()
    x_midas = hashlib.sha384(x_midas_base.encode()).hexdigest()
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://livecounts.io",
        "Referer": "https://livecounts.io/",
        "X-Ajay": x_ajay,
        "X-Catto": ts_str, # Catto IS the timestamp
        "X-Midas": x_midas,
    }
    
    if is_tiktok:
        # TikTok (tokcounter) often has same headers but case can vary or slightly different hashes
        headers["X-Catto"] = ts_str
        headers["X-Ajay"] = hashlib.sha1(ts_str.encode()).hexdigest()
        
    return headers

def send_request(url: str) -> dict[str, Any]:
    try:
        is_tiktok = "tokcounter.com" in url
        now_ms = int(datetime.now().timestamp() * 1000)
        # Random sleep to avoid rate limiting
        headers = __get_default_header(now_ms, is_tiktok)
        response = http_client.get(url=url, headers=headers)
        if response.status_code != 200:
            raise RequestApiError(f"HTTP ERROR {response.status_code}")
        data = msgspec.json.decode(response.content)
        if not data.get("success", True):
            raise RequestApiError("API Failed")
        return data
    except Exception as e:
        raise RequestApiError(str(e))

# --- Agents ---

class TiktokUser:
    def __init__(self, user_id: str, username: str, display_name: str, thumbnail: str, verified: bool = False):
        self.user_id, self.username, self.display_name, self.thumbnail, self.verified = user_id, username, display_name, thumbnail, verified

class TiktokAgent:
    def find_user(self, query: str) -> list[TiktokUser]:
        data = send_request(f"{TIKTOK_USER_SEARCH_API}/{quote(query)}")
        return [TiktokUser(i.get("userId", ""), i.get("id", ""), i.get("username", ""), i.get("avatar", ""), i.get("verified", False)) for i in data.get("userData", [])]
    
    def fetch_user_metrics(self, query: str):
        m = send_request(f"{TIKTOK_USER_STATS_API}/{quote(query)}")
        return {"followers": m.get("followerCount", 0), "likes": m.get("likeCount", 0), "following": m.get("followingCount", 0), "videos": m.get("videoCount", 0)}

class YoutubeAgent:
    def find_channel(self, query: str):
        data = send_request(f"{YOUTUBE_CHANNEL_SEARCH_API}/{quote(query)}")
        # Check both 'list' and 'userData' keys as they vary by API version
        return data.get("list", data.get("userData", []))
    
    def find_video(self, query: str):
        data = send_request(f"{YOUTUBE_VIDEO_SEARCH_API}/{quote(query)}")
        return data.get("list", data.get("userData", []))

class LivecountsAPI:
    def __init__(self):
        self.tiktok = TiktokAgent()
        self.youtube = YoutubeAgent()

api = LivecountsAPI()
